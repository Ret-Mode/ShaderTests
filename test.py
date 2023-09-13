import array
import arcade
from arcade.gl import BufferDescription
from arcade import ArcadeContext
import pyglet.gl
import random
import time


class Time:

    def __init__(self):
        self.time: float = 0.0
        self.measures: int = 0

    def startMeasure(self):
        self.time -= time.time()

    def stopMeasure(self):
        self.time += time.time()
        self.measures += 1

    def __repr__(self):
        return f'Cummulative:\t{self.time} Mean:\t{self.time/self.measures if self.measures != 0 else self.time}.'


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
                                   255, 0, 0, 255,
                                   255, 200, 0, 255,
                                   255, 0, 0, 255])
        self.colors = ctx.buffer(data=colors)
        colorsDescription = BufferDescription(self.colors, '4f1', ['inColor'], normalized=('inColor'))

        indices = array.array('I', [0,1,2,1])
        self.indexBuffer = ctx.buffer(data=indices)

        self.geometry = ctx.geometry([vertsDescription, colorsDescription], 
                                     index_buffer=self.indexBuffer, 
                                     mode=ctx.LINES)
        ctx.enable(pyglet.gl.GL_LINE_SMOOTH)
        self.time = Time()

    def draw(self):
        # self.time.startMeasure()
        # self.indexBuffer.write(data=array.array('I', [random.randint(0,3), random.randint(0,3), random.randint(0,3), random.randint(0,3)]))
        self.geometry.render(self.program)
        # print(self.time)


class Runner(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.lineDraw = LineDraw(self.ctx)

    def on_draw(self):
        self.clear()
        self.lineDraw.draw()


Runner(800, 600, "ShaderTest").run()