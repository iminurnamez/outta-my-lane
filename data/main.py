from . import prepare,tools
from .states import splash_screen, title_screen, gameplay, choose_vehicle, controls_screen

def main():
    controller = tools.Control(prepare.ORIGINAL_CAPTION)
    states = {"TITLE": title_screen.TitleScreen(),
                   "GAMEPLAY": gameplay.Gameplay(),
                   "SPLASH": splash_screen.SplashScreen(),
                   "CHOOSE_VEHICLE": choose_vehicle.ChooseVehicle(),
                   "CONTROLS_SCREEN": controls_screen.ControlsScreen()}
    controller.setup_states(states, "SPLASH")
    controller.main()
