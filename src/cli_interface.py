class CliInterface:
    @staticmethod
    def colorize(string, bold=False, red=False, yellow=False, green=False, cyan=False):
        """
        Return a string with bold, red, and/or yellow formatting. If many colors are specified, the color precedence is:
        red > yellow > green > cyan.
        :param string: The input string.
        :param bold: Whether to use bold formatting.
        :param red: Whether to use red formatting.
        :param yellow: Whether to use yellow formatting.
        :param green: Whether to use green formatting.
        :param cyan: Whether to use cyan formatting.
        """
        b = "\033[1m" if bold else ""
        r = "\033[91m" if red else ""
        y = "\033[93m" if yellow else ""
        g = "\033[92m" if green else ""
        c = "\033[96m" if cyan else ""
        e = "\033[0m"

        return f"{b}{c}{g}{y}{r}{string}{e}"

    @staticmethod
    def print_welcome():
        print("\n--------------------------------------------")
        print("| " + CliInterface.colorize("Welcome to the Whisper Audio Transcriber", bold=True) + " |")
        print("--------------------------------------------")

    @staticmethod
    def print_exit():
        print("\r\nExiting application...")
        print("\n-------------------------------------------------")
        print("| " + CliInterface.colorize("Thank you for using Whisper Audio Transcriber", bold=True) + " |")
        print("-------------------------------------------------")

    @staticmethod
    def print_error(e):
        print("\n" + CliInterface.colorize("!", red=True) + f" Error: {e}")

    @staticmethod
    def print_warning(message):
        print("\n" + CliInterface.colorize("⚠", yellow=True) + f" {message}")

    @staticmethod
    def print_success(message):
        print("\n" + CliInterface.colorize("✔", green=True) + f" {message}")

    @staticmethod
    def print_info(message):
        print("\n" + CliInterface.colorize("i", cyan=True) + f" {message}")

    @staticmethod
    def format_question(question):
        return CliInterface.colorize("?", bold=True) + f" {question}"

    @staticmethod
    def print_question(question):
        print("\n" + CliInterface.format_question(question))

    @staticmethod
    def print_error_message(message):
        print("\n" + CliInterface.colorize("!", red=True) + f" {message}")


start_pause_message = (
    "Press "
    + CliInterface.colorize("Space", bold=True)
    + " to start/pause recording."
    + " Press "
    + CliInterface.colorize("Esc", bold=True)
    + " to exit."
)
