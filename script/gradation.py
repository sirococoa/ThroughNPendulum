import sys

def gradation(start_color, end_color, steps):
    def interpolate(start, end, factor):
        return int(start + (end - start) * factor)

    gradation = []
    for i in range(steps):
        factor = i / (steps - 1)
        r = interpolate((start_color >> 16) & 0xFF, (end_color >> 16) & 0xFF, factor)
        g = interpolate((start_color >> 8) & 0xFF, (end_color >> 8) & 0xFF, factor)
        b = interpolate(start_color & 0xFF, end_color & 0xFF, factor)
        gradation.append((r << 16) | (g << 8) | b)
    return tuple(gradation)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python gradation.py <start_color> <end_color> <steps>")
        sys.exit(1)
    try:
        start_color = int(sys.argv[1], 16)
        end_color = int(sys.argv[2], 16)
        steps = int(sys.argv[3])
    except ValueError:
        print("Invalid input. Please provide valid hex colors and an integer for steps.")
        sys.exit(1)
    if steps < 2:
        print("Steps must be at least 2.")
        sys.exit(1)
    gradation_list = gradation(start_color, end_color, steps)
    print(", ".join(map(hex, gradation_list)))
