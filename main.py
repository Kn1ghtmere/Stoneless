import sys

from lock.platform_tools import compositor_warning,describe,enable_dpi_awareness


def main():
    enable_dpi_awareness()

    from ui import App
    print("stoneless running on",describe())
    warning=compositor_warning()
    if warning:
        print(warning)

    App(minimized="--minimized" in sys.argv).run()


if __name__=="__main__":
    main()