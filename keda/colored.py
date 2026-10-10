class __TEXT():
    def __init__(self):
        self.RED = '\033[31m'
        self.BLUE = '\033[34m'
        self.YELLOW = '\033[33m'
        self.MAGENTA = '\033[35m'
        self.CYAN = '\033[36m'
        self.GREEN = '\033[32m'
        self.RESET = '\033[0m'

    def red_text(self, txt:str):
        return f"{self.RED}{txt}{self.RESET}"

    def blue_text(self, txt:str):
        return f"{self.BLUE}{txt}{self.RESET}"

    def yellow_text(self, txt:str):
        return f"{self.YELLOW}{txt}{self.RESET}"

    def magenta_text(self, txt:str):
        return f"{self.MAGENTA}{txt}{self.RESET}"

    def cyan_text(self, txt:str):
        return f"{self.CYAN}{txt}{self.RESET}"

    def green_text(self, txt:str):
        return f"{self.GREEN}{txt}{self.RESET}"




Text =__TEXT()

