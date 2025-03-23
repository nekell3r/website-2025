class Rectangle:
    a: float
    b: float
    c: float
    d: float

    def __init__(self, first: tuple[float, float], second: tuple[float, float]):
        self.a = first[0]
        self.c = first[1]
        self.b = second[0]
        self.d = second[1]

    def area(self) -> float:
        return round(abs(self.a - self.b) * abs(self.c - self.d), 2)

    def perimeter(self) -> float:
        return round(2 * (abs(self.a - self.b) + abs(self.c - self.d)), 2)

    def resize(self, width: float, height: float):
        self.b = self.a + width
        self.d = self.c + height


rect = Rectangle((7.52, -4.3), (3.2, 3.14))
print(rect.area())
