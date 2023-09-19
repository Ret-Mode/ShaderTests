import array
import arcade
from arcade.gl import BufferDescription
from arcade import ArcadeContext
import pyglet.gl
import random
import time

from typing import List


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
        self.lineDraw = TextureDraw(self.ctx)
        self.sprite = arcade.Sprite("./pinky.png", 1.0)

    def on_draw(self):
        self.clear()
        self.sprite.draw()
        self.lineDraw.draw()


Runner(800, 600, "ShaderTest").run()