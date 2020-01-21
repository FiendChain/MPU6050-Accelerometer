class Vector3D:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __radd__(self, other):
        if not isinstance(other, Vector3D):
            return Vector3D(self.x+other, self.y+other, self.z+other)
        return self + other

    def __add__(self, other):
        return Vector3D(self.x+other.x, self.y+other.y, self.z+other.z)

    def __sub__(self, other):
        return Vector3D(self.x-other.x, self.y-other.y, self.z-other.z)
    
    def __mul__(self, k):
        return Vector3D(self.x*k, self.y*k, self.z*k)

    def __rmul__(self, k):
        return self * k

    def __rdiv__(self, k):
        return Vector3D(k/self.x, k/self.y, k/self.z)
    
    def __truediv__(self, k):
        return Vector3D(self.x/k, self.y/k, self.z/k)
    
    def __floordiv__(self, k):
        return Vector3D(self.x//k, self.y//k, self.z//k)

    def __str__(self):
        return f'{self.x:+.02f} {self.y:+.02f} {self.z:+.02f}'

    def __format__(self, fmt):
        return f'{self.x:{fmt}} {self.y:{fmt}} {self.z:{fmt}}'