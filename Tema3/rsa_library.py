import random

prime_number_1 = 277
prime_number_2 = 239

ON_low = '0x01'
NOT_low = '0xfe'

''' The plaintext can't be larger than the modulus'''
'''
Euclid's algorithm for determining the greatest common divisor
Use iteration to make it faster for larger integers
'''


def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


'''
Euclid's extended algorithm for finding the multiplicative inverse of two numbers
'''


def multiplicative_inverse(e, phi):
    d = 0
    x1 = 0
    x2 = 1
    y1 = 1
    temp_phi = phi

    while e > 0:
        temp1 = temp_phi // e
        temp2 = temp_phi - temp1 * e
        temp_phi = e
        e = temp2

        x = x2 - temp1 * x1
        y = d - temp1 * y1

        x2 = x1
        x1 = x
        d = y1
        y1 = y

    if temp_phi == 1:
        return d + phi


'''
Tests to see if a number is prime.
'''


def is_prime(num):
    if num == 2:
        return True
    if num < 2 or num % 2 == 0:
        return False
    for n in range(3, int(num ** 0.5) + 2, 2):
        if num % n == 0:
            return False
    return True


def generate_keypair(p, q):
    if not (is_prime(p) and is_prime(q)):
        raise ValueError('Both numbers must be prime.')
    elif p == q:
        raise ValueError('p and q cannot be equal')
    # n = pq
    modulus = p * q

    # Phi is the totient of n
    L = (p - 1) * (q - 1)
    # print("L=",L)

    # Choose an integer e such that e and L(n) are coprime
    e = random.randrange(2, L)
    # print('E=',e)

    # Use Euclid's Algorithm to verify that e and L(n) are comprime
    g = gcd(e, L)
    # print('G=',g)
    while g != 1:
        e = random.randrange(2, L)
        # print("E=",e)
        g = gcd(e, L)
        # print("G=",g)
    # Use Extended Euclid's Algorithm to generate the private key
    d = multiplicative_inverse(e, L)
    # print("D=",d)

    # Return public and private keypair
    # Public key is (e, n) and private key is (d, n)
    return ((e, modulus), (d, modulus))


############################### EXERCISE 1 ###############################
def encrypt(public_key, hex_number):
    hex_number = int(hex_number, 16)
    return hex((hex_number ** public_key[0]) % public_key[1])


############################### EXERCISE 2 ###############################
def decrypt(private_key, encrypted_msg):
    encrypted_msg = int(encrypted_msg, 16)
    return hex((encrypted_msg ** private_key[0]) % private_key[1])


############################### EXERCISE 3 ###############################
def low_check(hex_nr):
    hex_nr = int(hex_nr, 16)
    Low = int(ON_low, 16)
    if (hex_nr & 0xFF) == Low:
        return True
    else:
        return False


############################### EXERCISE 4 ###############################
def number_check(hex_nr):
    hex_nr = int(hex_nr, 16)
    High = int(NOT_low, 16)
    hex = (hex_nr >> 8) & High

    if hex == High:
        return True
    else:
        return False


(pk, sk) = generate_keypair(prime_number_1, prime_number_2)
enc = encrypt(pk, "0xFE01")
print(enc)
dec = decrypt(sk, enc)
print(dec)
print(low_check('0xfe01'))
print(number_check('0xfe01'))
