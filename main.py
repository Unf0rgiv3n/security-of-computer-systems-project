from app.gui import gui
from app.encryption import key_gens

if __name__ == "__main__":
    key_gens.generate_keys()
    app = gui.Gui("BSK - 180189, 180544")
    app.mainloop()