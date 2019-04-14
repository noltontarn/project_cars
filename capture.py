import pygame
import mss
import time

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)

# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def print(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height
        
    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15
        
    def indent(self):
        self.x += 10
        
    def unindent(self):
        self.x -= 10
    

pygame.init()
 
# Set the width and height of the screen [width,height]
size = [500, 700]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("My Game")

#Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Initialize the joysticks
pygame.joystick.init()
    
# Get ready to print
textPrint = TextPrint()

axisX = 0
axisY = 0
start = False
ButtonPress = -1
Button0 = 0
Button6 = 0
Button7 = 0
start_time = time.time()
previous_time = start_time
sct = mss.mss()
f = open('input_half_monza2.txt', 'w')
id = 1
# -------- Main Program Loop -----------
while done==False:
    # EVENT PROCESSING STEP
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            end_time = time.time()
            print('running time', str(end_time - start_time))
            done=True # Flag that we are done so we exit this loop
        
        # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
        if event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed.")
        if event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")
            
 
    # DRAWING STEP
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(WHITE)
    textPrint.reset()

    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()

    textPrint.print(screen, "Number of joysticks: {}".format(joystick_count) )
    textPrint.indent()
    
    # For each joystick:
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
    
        textPrint.print(screen, "Joystick {}".format(i) )
        textPrint.indent()
        j = i
        # Get the name from the OS for the controller/joystick
        name = joystick.get_name()
        textPrint.print(screen, "Joystick name: {}".format(name) )
        
        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()
        textPrint.print(screen, "Number of axes: {}".format(axes) )
        textPrint.indent()
        
        for i in range( axes ):
            axis = joystick.get_axis( i )
            textPrint.print(screen, "Axis {} value: {:>6.3f}".format(i, axis) )
            if i == 0 and j == 0:
                axisX = axis
            elif i == 1 and j ==0:
                axisY = axis
        textPrint.unindent()
            
        buttons = joystick.get_numbuttons()
        textPrint.print(screen, "Number of buttons: {}".format(buttons) )
        textPrint.indent()

        for i in range( buttons ):
            button = joystick.get_button( i )
            textPrint.print(screen, "Button {:>2} value: {}".format(i,button) )
            if button == 1:
                print("Button {:>2} value: {}".format(i,button) )
                ButtonPress = i
            if ButtonPress == 10 and start == False:
                start = True
                print("start recording...")
            if ButtonPress == 11 and start == True:
                start = False
                print("stop recording...")
            if ButtonPress == 10 or ButtonPress == 11:
                ButtonPress = -1
        textPrint.unindent()
            
        # Hat switch. All or nothing for direction, not like joysticks.
        # Value comes back in an array.
        hats = joystick.get_numhats()
        textPrint.print(screen, "Number of hats: {}".format(hats) )
        textPrint.indent()

        for i in range( hats ):
            hat = joystick.get_hat( i )
            textPrint.print(screen, "Hat {} value: {}".format(i, str(hat)) )
        textPrint.unindent()
        
        textPrint.unindent()
    #if time.time() - previous_time >= (1/66):
        #previous_time = time.time()
    if start == True:
        name = "./input_half_monza2/" + str(id) + ".png"
        if ButtonPress == 0:
            Button0 = 1
        if ButtonPress == 6:
            Button6 = 1
        if ButtonPress == 7:
            Button7 = 1
        print("{}, {}, {}, {}, {}, {}\n".format(axisX, axisY, Button0, Button6, Button7, time.time() - start_time))
        f.write("{}, {}, {}, {}, {}, {}\n".format(name, axisX, axisY, Button0, Button6, Button7))
        #image = sct.shot( output = name)
        #monitor = {"top": 272, "left": 570, "width": 800, "height": 600}
        monitor = {"top": 272, "left": 570, "width": 798, "height": 300}
        output = name.format(**monitor)

    # Grab the data
        sct_img = sct.grab(monitor)

    # Save to the picture file
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
        id += 1

    ButtonPress = -1
    Button0 = 0
    Button6 = 0
    Button7 = 0
    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
    
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # Limit to 60 frames per second
    clock.tick()
    
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit ()
