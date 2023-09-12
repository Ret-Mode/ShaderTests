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
            in vec2 in_vert;

            void main() {
                gl_Position = vec4(in_vert.x, in_vert.y, 0.0, 1.0);
            }
            """

        fragmentShader="""
            #version 330

            out vec4 out_color;

            void main() {
                out_color = vec4(1.0, 0.5, 0.2, 1.0);
            }
            """
        self.program = ctx.program(vertex_shader=vertexShader, fragment_shader=fragmentShader)
        self.data = array.array('f', [
                        -0.5, -0.5,
                        0.5, -0.5,
                        0.5, 0.5,
                        -0.5,  0.5,
        ])
        self.buffer = ctx.buffer(data=self.data)
        self.indexBuffer = ctx.buffer(data=array.array('I', [0,1,2,3]))
        self.bufferDescription = BufferDescription(self.buffer, '2f', ['in_vert'] )
        self.geometry = ctx.geometry([self.bufferDescription], index_buffer=self.indexBuffer, mode=ctx.LINES)
        ctx.enable(pyglet.gl.GL_LINE_SMOOTH)
        self.time = Time()

    def draw(self):
        self.time.startMeasure()
        self.indexBuffer.write(data=array.array('I', [random.randint(0,3), random.randint(0,3), random.randint(0,3), random.randint(0,3)]))
        self.time.stopMeasure()
        self.geometry.render(self.program)
        print(self.time)


class Runner(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.lineDraw = LineDraw(self.ctx)

    def on_draw(self):
        self.clear()
        self.lineDraw.draw()


Runner(800, 600, "SHaderTest").run()