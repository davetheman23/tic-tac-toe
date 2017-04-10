#!/usr/bin/env python

from view import visualizer


def main():
    vis = visualizer.Visualizer(None, [1, 2])

    vis.run()


if __name__ == '__main__':
    main()
