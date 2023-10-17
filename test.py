import array
import arcade
from arcade.gl import BufferDescription
from arcade import ArcadeContext
import pyglet.gl
import random

from typing import List


class RenderTarget:

    def __init__(self, ctx:arcade.ArcadeContext, width:int, height:int):
        vertexShader="""
            #version 330

            in vec2 inVert;

            uniform WindowBlock
            {
                mat4 projection;
                mat4 view;
            } window;  

            void main() {
                gl_Position = vec4(inVert.x+gl_InstanceID*0.1, inVert.y-gl_InstanceID*0.1, 0.0, 1.0);
            }
            """

        fragmentShader="""
            #version 330

            
            layout(location = 0) out vec4 f1Color;
            layout(location = 1) out vec4 f2Color;

            void main() {
                f1Color = vec4(1.0, 0.0, 0.0, 1.0);
                f2Color = vec4(0.0, 1.0, 0.0, 1.0);
            }
            """
        self.program = ctx.program(vertex_shader=vertexShader, fragment_shader=fragmentShader)
    
        self.fbo = ctx.framebuffer(
            color_attachments=[ctx.texture(size=(width, height)), ctx.texture(size=(width, height))]
        )
        verts = array.array('f', [
                        -1.0, -1.0, 1.0, 1.0
        ])
        self.verts = ctx.buffer(data=verts)
        vertsDescription = BufferDescription(self.verts, '2f', ['inVert'] )
        self.geometry = ctx.geometry([vertsDescription],
                                     mode=ctx.LINES)

    def resize(self, width, height):
        self.fbo.color_attachments[0].resize((int(width), int(height)))
        self.fbo.color_attachments[1].resize((int(width), int(height)))
        self.fbo.resize()

    def draw(self):
        with self.fbo.activate() as fbo:
            fbo.clear()
            self.geometry.render(self.program, instances=10)


class TextureDraw2:

    def __init__(self, ctx:arcade.ArcadeContext):
        vertexShader="""
            #version 330

            in vec2 inVert;
            in vec2 inUV;

            uniform WindowBlock
            {
                mat4 projection;
                mat4 view;
            } window;  

            out vec2 fUV;

            void main() {
                fUV = inUV;
                gl_Position = vec4(inVert.x+gl_InstanceID*0.1, inVert.y, 0.0, 1.0);
            }
            """

        fragmentShader="""
            #version 330

            in vec2 fUV;

            uniform sampler2D t1;
            uniform sampler2D t2;

            void main() {
                gl_FragColor = mix(texture(t1, fUV), texture(t2, fUV), fUV.x);
            }
            """
        self.program = ctx.program(vertex_shader=vertexShader, fragment_shader=fragmentShader)

        verts = array.array('f', [
                        -1.0, -1.0,
                        1.0, -1.0,
                        -1.0, 1.0,
                        1.0, 1.0
        ])
        
        self.verts = ctx.buffer(data=verts)
        vertsDescription = BufferDescription(self.verts, '2f', ['inVert'] )

        uvs = array.array('f', [0.0, 0.0,
                                   1.0, 0.0,
                                   0.0, 1.0,
                                   1.0, 1.0])
        self.uvs = ctx.buffer(data=uvs)
        colorsDescription = BufferDescription(self.uvs, '2f', ['inUV'])

        indices = array.array('I', [0,1,2,2,1,3])
        self.indices = ctx.buffer(data=indices)

        self.program.set_uniform_safe('t1', 0)
        self.program.set_uniform_safe('t2', 1)

        self.geometry = ctx.geometry([vertsDescription, colorsDescription], 
                                     index_buffer=self.indices, 
                                     mode=ctx.TRIANGLES)

    def draw(self, renderTarget:RenderTarget):
        renderTarget.fbo.color_attachments[0].use(0)
        renderTarget.fbo.color_attachments[1].use(1)
        self.geometry.render(self.program, instances=10)


class GridDraw:
    
    def __init__(self, ctx:ArcadeContext):
        vertexShader="""
            #version 330

            in vec2 inVert;

            uniform WindowBlock
            {
                mat4 projection;
                mat4 view;
            } window;  

            uniform ABC {
                vec4 color;
                vec2 delta;
            } abc;

            void main() {
                gl_Position = vec4(inVert.xy, 0.0, 1.0);
            }
            """

        geometryShader="""
            #version 330 core
            layout (points) in;
            layout (line_strip, max_vertices = 256) out;


            uniform ABC {
                vec4 color;
                vec2 delta;
            } abc;

            void main() {
                int dx;
                int dy;
                float fX = gl_in[0].gl_Position.x;
                float fY = gl_in[0].gl_Position.y;
                for (dx = 0; dx < 8; ++dx)
                {
                    for (dy = 0; dy < 8; ++dy)
                    {
                        
                        float x = fX + dx * abc.delta.x;
                        float y = fY + dy * abc.delta.y;

                        gl_Position = vec4(x-0.01, y, 0.0, 1.0); 
                        EmitVertex();

                        gl_Position = vec4(x+0.01, y, 0.0, 1.0); 
                        EmitVertex();
                        
                        EndPrimitive();

                        gl_Position = vec4(x, y-0.01, 0.0, 1.0); 
                        EmitVertex();

                        gl_Position = vec4(x, y+0.01, 0.0, 1.0); 
                        EmitVertex();
                        
                        EndPrimitive();
                    }
                }
            } 
            """

        fragmentShader="""
            #version 330

            uniform ABC {
                vec4 color;
                vec2 delta;
            } abc;

            out vec4 fColor;

            void main() {
                fColor = vec4(abc.color.rgb, 1.0);
            }
            """
        self.program = ctx.program(vertex_shader=vertexShader, geometry_shader=geometryShader, fragment_shader=fragmentShader)

        verts = array.array('f', [
                        -1.0, -1.0, -0.89, -0.89
        ])
        
        self.verts = ctx.buffer(data=verts)
        vertsDescription = BufferDescription(self.verts, '2f', ['inVert'] )

        indices = array.array('I', [0,0])
        self.indices = ctx.buffer(data=indices)

        uniform = array.array('f', [
                        1.0, 0.5, 1.0, 1.0, 0.1, 0.1, 0.0, 0.0])
        self.uniform = ctx.buffer(data=uniform)
        
        self.uniform.bind_to_uniform_block(1)

        self.program.set_uniform_safe('ABC', 1)
        # keep Window Block uniform
        self.program.set_uniform_safe('WindowBlock', 0)

        self.geometry = ctx.geometry([vertsDescription],
                                     mode=ctx.POINTS, 
                                     index_buffer=self.indices)
        #ctx.disable(pyglet.gl.GL_DEPTH_TEST)

    def updateVerts(self, verts:List[float]):
        vertsInBytes = len(verts) * 4
        if vertsInBytes != self.verts.size:
            self.verts.orphan(size=vertsInBytes)
        self.verts.write(array.array('f', verts))

        indices = [i for i in range(len(verts)//2)]
        indicesInBytes = len(indices) * 4
        if indicesInBytes != self.indices.size:
            self.indices.orphan(size=indicesInBytes)
            self.geometry.num_vertices = len(indices)
        self.indices.write(array.array('I', indices))

    def updateParams(self, deltas:List[float], color:List[float]):
        arr = color + [1.0] + deltas + [0.0, 0.0]
        self.uniform.write(array.array('f', arr))

    def draw(self):
        self.geometry.render(self.program)


class TextureDraw:

    def __init__(self, ctx:ArcadeContext):
        vertexShader="""
            #version 330

            in vec2 inVert;
            in vec2 inUV;

            out vec2 fUV;

            void main() {
                fUV = inUV;
                gl_Position = vec4(inVert.xy, 0.0, 1.0);
            }
            """

        fragmentShader="""
            #version 330

            in vec2 fUV;

            uniform sampler2D t1;
            uniform sampler2D t2;

            void main() {
                gl_FragColor = mix(texture(t1, fUV), texture(t2, fUV), 0.5);
            }
            """
        self.program = ctx.program(vertex_shader=vertexShader, fragment_shader=fragmentShader)

        verts = array.array('f', [
                        -0.5, -0.5,
                        0.5, -0.5,
                        0.0, 0.5
        ])
        
        self.verts = ctx.buffer(data=verts)
        vertsDescription = BufferDescription(self.verts, '2f', ['inVert'] )

        uvs = array.array('f', [0.0, 0.0,
                                   1.0, 0.0,
                                   0.5, 1.0])
        self.uvs = ctx.buffer(data=uvs)
        colorsDescription = BufferDescription(self.uvs, '2f', ['inUV'])

        indices = array.array('I', [0,1,2])
        self.indices = ctx.buffer(data=indices)

        self.texture1 = ctx.load_texture("pinky.png")
        self.texture2 = ctx.load_texture("wheel2.png")

        self.program.set_uniform_safe('t1', 0)
        self.program.set_uniform_safe('t2', 1)

        self.geometry = ctx.geometry([vertsDescription, colorsDescription], 
                                     index_buffer=self.indices, 
                                     mode=ctx.TRIANGLES)
        ctx.disable(pyglet.gl.GL_DEPTH_TEST)



    def updateIndices(self, indices:List[int]):
        indicesInBytes = len(indices) * 4
        if indicesInBytes != self.indices.size:
            self.indices.orphan(size=indicesInBytes)
        self.indices.write(array.array('I', indices))
        self.geometry.num_vertices = len(indices)

    def updateVerts(self, verts:List[float]):
        vertsInBytes = len(verts) * 4
        if vertsInBytes > self.verts.size:
            self.verts.orphan(size=vertsInBytes)
        self.verts.write(array.array('f', verts))

    def updateUVs(self, uvs:List[float]):
        uvsInBytes = len(uvs) * 4
        if uvsInBytes > self.uvs.size:
            self.uvs.orphan(size=uvsInBytes)
        self.uvs.write(array.array('f', uvs))

    def update(self, verts:List[float], uvs:List[float], indices:List[int]):
        vertsInBytes = len(verts) * 4
        uvsInBytes = len(uvs) * 4
        indicesInBytes = len(indices) * 4

        if vertsInBytes > self.verts.size:
            self.verts.orphan(size=vertsInBytes)
        self.verts.write(array.array('f', verts))
        
        if uvsInBytes > self.uvs.size:
            self.uvs.orphan(size=uvsInBytes)
        self.uvs.write(array.array('f', uvs))
        
        if indicesInBytes != self.indices.size:
            self.indices.orphan(size=indicesInBytes)
            self.geometry.num_vertices = len(indices)
        self.indices.write(array.array('I', indices))

    def draw(self):
        self.texture1.use(0)
        self.texture2.use(1)
        #self.updateIndices([random.randint(0,2) for i in range(30)])
        self.geometry.render(self.program)


class LineDraw:

    def __init__(self, ctx:ArcadeContext):
        vertexShader="""
            #version 330

            in vec2 inVert;
            in vec4 inColor;

            out vec4 fColor;

            void main() {
                fColor = inColor;
                gl_Position = vec4(inVert.xy, 0.0, 1.0);
            }
            """

        fragmentShader="""
            #version 330

            in vec4 fColor;

            void main() {
                gl_FragColor = vec4(fColor.rgb, 1.0);
            }
            """
        self.program = ctx.program(vertex_shader=vertexShader, fragment_shader=fragmentShader)

        verts = array.array('f', [
                        -0.5, -0.5,
                        0.5, -0.5,
                        0.5, 0.5,
                        -0.5,  0.5,
        ])
        
        self.verts = ctx.buffer(data=verts)
        vertsDescription = BufferDescription(self.verts, '2f', ['inVert'] )

        colors = array.array('B', [255, 0, 0, 255, 
                                   0, 255, 0, 255,
                                   0, 0, 255, 255,
                                   255, 255, 255, 255])
        self.colors = ctx.buffer(data=colors)
        colorsDescription = BufferDescription(self.colors, '4f1', ['inColor'], normalized=['inColor'])

        indices = array.array('I', [0,0])
        self.indices = ctx.buffer(data=indices)

        self.geometry = ctx.geometry([vertsDescription, colorsDescription], 
                                     index_buffer=self.indices, 
                                     mode=ctx.LINES)
        ctx.enable(pyglet.gl.GL_LINE_SMOOTH)
        ctx.disable(pyglet.gl.GL_DEPTH_TEST)
        print(self.verts.size)
        print(self.colors.size)
        print(self.indices.size)

    def updateIndices(self, indices:List[int]):
        indicesInBytes = len(indices) * 4
        if indicesInBytes != self.indices.size:
            self.indices.orphan(size=indicesInBytes)
        self.indices.write(array.array('I', indices))
        self.geometry.num_vertices = len(indices)

    def updateVerts(self, verts:List[float]):
        vertsInBytes = len(verts) * 4
        if vertsInBytes > self.verts.size:
            self.verts.orphan(size=vertsInBytes)
        self.verts.write(array.array('f', verts))

    def updateColors(self, colors:List[int]):
        colorsInBytes = len(colors)
        if colorsInBytes > self.colors.size:
            self.colors.orphan(size=colorsInBytes)
        self.colors.write(array.array('B', colors))

    def update(self, verts:List[float], colors:List[int], indices:List[int]):
        vertsInBytes = len(verts) * 4
        colorsInBytes = len(colors)
        indicesInBytes = len(indices) * 4

        if vertsInBytes > self.verts.size:
            self.verts.orphan(size=vertsInBytes)
        self.verts.write(array.array('f', verts))
        
        if colorsInBytes > self.colors.size:
            self.colors.orphan(size=colorsInBytes)
        self.colors.write(array.array('B', colors))
        
        if indicesInBytes != self.indices.size:
            self.indices.orphan(size=indicesInBytes)
            self.geometry.num_vertices = len(indices)
        self.indices.write(array.array('I', indices))

    def draw(self):
        self.updateIndices([random.randint(0,3) for i in range(30)])
        self.geometry.render(self.program)



class Runner(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        #self.atlas = arcade.TextureAtlas()
        #self.spriteList = arcade.SpriteList(atlas=self.atlas)
        #self.spriteList.append(arcade.Sprite("./pinky.png"))
        self.atlas = arcade.TextureAtlas((512,512), ctx = self.ctx)
        texture = arcade.load_texture("./pinky.png")
        self.spriteList = arcade.SpriteList(atlas=self.atlas)
        self.spriteList.append(arcade.Sprite(texture = texture))
        self.texture = self.spriteList.sprite_list[-1].texture
        self.spriteList.sprite_list[-1].set_position(120, 20)
        self.spriteList.append(arcade.Sprite(texture = texture))
        self.spriteList.sprite_list[-1].set_position(230, 30)
        self.spriteList.append(arcade.Sprite(texture = texture))
        self.spriteList.sprite_list[-1].set_position(340, 40)
        self.spriteList.append(arcade.Sprite("./wheel2.png"))
        

        self.rt = RenderTarget(self.ctx, width, height)
        self.shader = TextureDraw2(self.ctx)

    def on_resize(self, width: float, height: float):
        self.rt.resize(width, height)
        return super().on_resize(width, height)
    
    def on_draw(self):
        self.clear()
        self.rt.draw()
        self.shader.draw(self.rt)
        ## region = self.atlas.get_region_info(self.texture.name)
        self.spriteList.draw()
        #self.ctx.sprite_list_program_cull
        #self.ctx.default_atlas


Runner(800, 600, "ShaderTest").run()