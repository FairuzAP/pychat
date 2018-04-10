import math
import sys
import pickle
import random
from Point import Point


class EllipticCurve:
    """
    API for manipulating a discrete elliptic curve in Galois Field GP(p)
    """

    @staticmethod
    def is_quadratic_residue(a, p):
        """
        Legendre symbol (http://en.wikipedia.org/wiki/Legendre_symbol)
        Define if a is a quadratic residue modulo odd prime
        """
        ls = pow(int(a), int((p - 1) / 2), p)
        if ls == p - 1:
            return -1
        return ls

    @staticmethod
    def tonelli_shanks(a, p):
        """
        Square root modulo prime number (http://en.wikipedia.org/wiki/Tonelli-Shanks_algorithm)
        Solve the equation [ x^2 = a mod p ] and return list of x solution
        """
        a %= p

        # Simple case
        if a == 0:
            return [0]
        if p == 2:
            return [a]

        # Check solution existence on odd prime
        if EllipticCurve.is_quadratic_residue(a, p) != 1:
            return []

        # Simple case
        if p % 4 == 3:
            x = pow(int(a), int((p + 1) / 4), p)
            return [x, p - x]

        # Factor p-1 on the form q * 2^s (with Q odd)
        q, s = p - 1, 0
        while q % 2 == 0:
            s += 1
            q //= 2

        # Select a z which is a quadratic non residue modulo p
        z = 1
        while EllipticCurve.is_quadratic_residue(z, p) != -1:
            z += 1
        c = pow(z, q, p)

        # Search for a solution
        x = pow(a, (q + 1) / 2, p)
        t = pow(a, q, p)
        m = s
        while t != 1:
            # Find the lowest i such that t^(2^i) = 1
            i, e = 0, 2
            for i in range(1, m):
                if pow(t, e, p) == 1:
                    break
                e *= 2

            # Update next value to iterate
            b = pow(c, 2 ** (m - i - 1), p)
            x = (x * b) % p
            t = (t * b * b) % p
            c = (b * b) % p
            m = i

        return [x, p - x]

    def __init__(self, a, b, p):
        """
        Initialize the elliptic curve parameter of y^2 (mod p) = x^3 + ax + b (mod p)
        :param p: Must be a prime number
        """
        self.a = a
        self.b = b
        self.p = p

    def get_y(self, x):
        """
        Return the y coord list of the given x coord in the elliptic curve
        :param x: The x point of the elliptic curve
        :return: Array of possible y coord. in the given x coord.
        """
        if x < 0 or x >= self.p:
            return []

        n = x**3 + self.a * x + self.b
        return EllipticCurve.tonelli_shanks(n, self.p)

    def is_valid(self, point):
        """
        Return whether or not the given point is in this curve
        :param point: The point to be checked
        :return: Wether or not the given point is a valid point in this curve
        """
        y_list = self.get_y(point.X)
        if not y_list:
            return False

        for y in y_list:
            if point.Y == y:
                return True

        return False

    def add_point(self, pa, pb):
        """
        Return the result of elliptic curve point addition.
        PA and PB must exist in the curve
        :param pa: A valid point in this curve
        :param pb: A valid point in this curve
        :return: A valid point in the curve that is the result of pa + pb
        """
        if pa.X == pb.X and pa.Y == pb.Y:
            return self.double_point(pa)
        elif pa.X == pb.X:
            return Point(math.inf, math.inf)
        elif pa.X == math.inf:
            return pb
        elif pb.X == math.inf:
            return pa

        if (pa.X - pb.X) > 0:
            xp = pa.X; yp = pa.Y
            xq = pb.X; yq = pb.Y
        else:
            xp = pb.X; yp = pb.Y
            xq = pa.X; yq = pa.Y

        dy = yp - yq
        dx = xp - xq

        # TODO change the inverse modulo calculation to using Extended Euclidean instead of Euler's
        dxi = pow(int(dx), int(self.p - 2), self.p)

        m = (dy * dxi) % self.p

        xr = (m**2 - xp - xq) % self.p
        yr = (m * (xp - xr) - yp) % self.p

        return Point(xr, yr)

    def subtract_point(self, pa, pb):
        """
        Return the result of elliptic curve point subtractions
        PA and PB must exist in the curve
        :param pa: A valid point in this curve
        :param pb: A valid point in this curve
        :return: A valid point in the curve that is the result of pa - pb
        """
        n_pb = Point(pb.X, ((-pb.Y) % self.p))
        return self.add_point(pa, n_pb)

    def double_point(self, pa):
        """
        Return the result of elliptic curve point duplication.
        :param pa: A valid point in this curve
        :return: A valid point in the curve that is the result of 2*pa
        """
        if pa.Y == 0:
            return Point(math.inf, math.inf)
        elif pa.X == math.inf:
            return pa

        dy = 3*(pa.X**2) + self.a
        dx = 2*pa.Y

        # TODO change the inverse modulo calculation to using Extended Euclidean instead of Euler's
        dxi = pow(int(dx), int(self.p - 2), self.p)

        m = (dy * dxi) % self.p

        xr = (m**2 - 2*pa.X) % self.p
        yr = (m * (pa.X - xr) - pa.Y) % self.p

        return Point(xr, yr)

    def iterate_point(self, pa, k):
        """
        Return the result of elliptic curve point duplication.
        :param pa: A valid point in this curve
        :return: A valid point in the curve that is the result of k * pa
        """
        if k == 1:
            return pa

        elif k % 2 == 0:
            return self.iterate_point(
                self.double_point(pa),
                k / 2
            )

        elif k % 2 == 1:
            return self.add_point(
                pa,
                self.iterate_point(
                    self.double_point(pa),
                    (k - 1) / 2
                )
            )

    def get_order(self, p):
        """
        :param p: A valid point in the curve
        :return: The order of p
        """
        k = 2
        while True:
            p_k = self.iterate_point(p, k)
            if p_k.X == math.inf:
                return k
            k += 1


class ECCipher:
    """
    API for ECC encrypting and decrypting of byte array
    """

    def __init__(self, a, b, p, g, k=20):
        """
        Initialize the cipher with the given parameter
        :param a, b, p: The curve 'y^2 (mod p) = x^3 + ax + b (mod p)' parameter
        :param g: The generator point which is a valid point in the given curve
        :param k: The auxiliary base parameter used for message encoding and decoding
        """
        self.a = a
        self.b = b
        self.p = p
        self.curve = EllipticCurve(a, b, p)
        self.g = g
        self.k = k

        self.encode = []
        for byte in range(256):

            for i in range(1, self.k):
                x = byte * self.k + i
                ys = self.curve.get_y(x)

                if ys:
                    self.encode.append(Point(x, ys[i % 2]))
                    break

                elif i == self.k - 1:
                    sys.exit("Well this is unfortunate")

    def gen_key_pair(self):
        """
        :return: private key, public key tuple
        """
        sk = random.randint(0, self.p - 1)
        pk = self.curve.iterate_point(self.g, a)
        return sk, pk

    def gen_partial_key_n(self, sk, n):
        """
        :param sk: A private key array with value 1 < a < p-1
        :param n: The size of the key array
        :return: A partial Diffie-Hellman key array
        """
        return [self.curve.iterate_point(self.g, sk[i]) for i in range(n)]

    def gen_shared_key_n(self, a, pt, n):
        """
        Generate a shared secret point from the given private key and partial key
        :param a: A private key array with value 1 < a < p-1
        :param pt: A partial Diffie-Hellman key array
        :param n: The size of the key array
        :return: The shared secret point array
        """
        return [self.curve.iterate_point(pt[i], a[i]) for i in range(n)]

    def gen_fancy_des_secret_key(self):
        return [random.randint(0, self.p - 1) for _ in range(4)]

    def gen_fancy_des_partial_key(self, sk):
        pt = self.gen_partial_key_n(sk, 4)
        return ECCipher.dump_points(pt)

    def gen_fancy_des_shared_key(self, sk, ptb):
        pt = ECCipher.load_points(ptb)
        sc = self.gen_shared_key_n(sk, pt, 4)
        res = []
        for i in range(4):
            res.extend((sc[i].X % 4294967296).to_bytes(4, byteorder='big'))
            res.extend((sc[i].Y % 4294967296).to_bytes(4, byteorder='big'))
        return res

    def plain_encode(self, byte_arr):
        """
        Convert the given bytes array to an array of point
        :param byte_arr: A valid bytes array / int array where each element value is between 0-255
        :return: The point encoding of the given bytes array using Koblitz’s Method
        """
        ret = []
        for m in byte_arr:
            ret.append(self.encode[m])

        return ret

    def plain_decode(self, point_arr):
        """
        Convert the given point array to an array of bytes
        :param point_arr: A valid point array where each element exist in the curve used
        :return: The bytes decoding of the given point array using Koblitz’s Method
        """
        ret = []
        for point in point_arr:
            m = math.floor((point.X - 1) / self.k)
            ret.append(m)
        return bytes(ret)

    @staticmethod
    def dump_points(enc_point_arr):
        return pickle.dumps(enc_point_arr, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_points(byte_arr):
        return pickle.loads(byte_arr)

    def encrypt(self, point_arr, pb, k=None):
        """
        Encrypt the given point array using El Gamal algorithm
        :param point_arr: A point array where each point is valid in this cipher's curve
        :param pb: The public key of the intended recipient, which is a valid point in this cipher's curve
        :param k: A random number used for this encryption, will be generated if none supplied
        :return: An encrypted point array (The 0'th element contains partial key value)
        """
        if k is None:
            k = random.randint(0, self.p - 1)

        kb = self.curve.iterate_point(pb, k)
        ret = [self.curve.iterate_point(self.g, k)]
        for pm in point_arr:
            ret.append(
                self.curve.add_point(pm, kb)
            )
        return ret

    def decrypt(self, enc_point_arr, b):
        """
        Decrypt the given encrypted point array using El Gamal algorithm
        :param enc_point_arr: A valid encrypted point array
        :param b: The private key of the intended recipient
        :return: A point array that has been encrypted
        """
        bkb = self.curve.iterate_point(enc_point_arr[0], b)
        ret = []
        for pc in enc_point_arr[1:]:
            ret.append(
                self.curve.subtract_point(pc, bkb)
            )
        return ret


def main():
    curve = EllipticCurve(1,1,23)
    for i in range(23):
        print(i, " -> ", curve.get_y(i))
    print(curve.add_point(Point(0,1), Point(1,7)))
    for i in range(50):
        print(i + 1, " -> ", curve.iterate_point(Point(0, 1), i + 1))

    cipher = ECCipher(-1, 188, 7919, Point(224, 503), 20)

    sk_a = cipher.gen_fancy_des_secret_key()
    sk_b = cipher.gen_fancy_des_secret_key()

    ptb_a = cipher.gen_fancy_des_partial_key(sk_a)
    ptb_b = cipher.gen_fancy_des_partial_key(sk_b)

    sh_a = cipher.gen_fancy_des_shared_key(sk_a, ptb_b)
    sh_b = cipher.gen_fancy_des_shared_key(sk_b, ptb_a)

    assert sh_a == sh_b

    countries = ["Argentina", "Australia", "Austria", "Bahrain", "Belgium", "Brazil", "Canada", "China", "Croatia", "Czech Republic", "Denmark", "Dominican Rep.", "Egypt", "Finland", "France", "Germany", "Greece", "Hong Kong, China", "Hungary", "India", "Indonesia", "Ireland", "Italy", "Japan", "Jordan", "Korea (Rep.)", "Macao, China", "Malaysia", "Mexico", "Morocco", "Netherlands", "Norway", "Poland", "Portugal", "Romania", "Russian Federation", "Saudi Arabia", "Singapore", "South Africa", "Spain", "Sweden", "Switzerland", "Thailand", "Tunisia", "Turkey", "United Arab Emirates", "United Kingdom", "United States", "Viet Nam", "Zimbabwe"]
    json = ""
    for country in countries:
        json += '{\n      "id": "' + country + '",\n      "text": "' + country + '"\n    }, '
    print(json)

if __name__ == "__main__":
    main()