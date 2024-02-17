import moving_a_sprite_along_with_a_catmull_rom_spline as xxx


def calc_factors(control_points):
    p0, p1, p2, p3 = control_points
    return (
        (p0 + p2) / 6.0 + p1 * 2.0 / 3.0,
        (p2 - p0) * 0.5,
        (p0 + p2) * 0.5 - p1,
        (p3 - p0) / 6.0 + (p1 - p2) * 0.5,
    )


xxx.calc_factors = calc_factors


if __name__ == '__main__':
    xxx.SampleApp(title="Moving a aprite along with a B-Splie").run()
