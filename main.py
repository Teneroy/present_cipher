from bitarray import bitarray

s_mapping = {
    '0':'C', '1':'5', '2':'6', '3':'B', '4':'9', '5':'0', '6':'A', '7':'D',
    '8':'3', '9':'E', 'A':'F', 'B':'8', 'C':'4', 'D':'7', 'E':'1', 'F':'2'
}

INT_BITS = 32
# Function to left
# rotate n by d bits
def leftRotate(n, d):
    # In n<<d, last d bits are 0.
    # To put first 3 bits of n at
    # last, do bitwise or of n<<d
    # with n >>(INT_BITS - d)
    return (n << d) | (n >> (80 - d))


def transform_to_hex_arr(str_num):
    arr = []
    for number in str_num:
        arr.append(hex(int(number, 16)))
    return arr


def transform_hex_arr_to_str(arr):
    hex_str = ''
    for elem in arr:
        hex_str += str(elem).split('0x')[1]
    return hex_str


def transform_str_to_bitarray(str_num):
    str_bits = ''
    for num in str_num:
        n = int(num, 16)
        str_bits += '{0:04b}'.format(n)
    return bitarray(str_bits)


def transform_bitarray_to_str(bits):
    result = ''
    for i in range(0, len(bits), 4):
        bit_chunk = bits[i:(i + 4)]
        hex_symbol = hex(int(bit_chunk.to01(), 2)).split('0x')[1]
        result += hex_symbol.upper()
    return result


def update_key(key, round_counter):
    K = transform_to_hex_arr(key)
    K_bit_str = ''
    for num in K:
        n = int(num, 16)
        K_bit_str += '{0:04b}'.format(n)

    K_bit = bitarray(K_bit_str)
    #Step 1 rotate
    K_bit = leftRotate(K_bit, 61)

    #Step 2 s_box
    leftmost_four = K_bit[:4]
    leftmost_four_changed = s_box(leftmost_four)
    K_bit = K_bit[4:]
    for i in range(len(leftmost_four_changed)):
        K_bit.insert(i, leftmost_four_changed[i])

    #Step 3 rounding
    rounding_bits = K_bit[60:65]
    round_counter_bits = bitarray('{0:05b}'.format(round_counter))
    rounding_result = bitarray()
    for i in range(len(rounding_bits)):
        rounding_result.append(bool(rounding_bits[i]) != bool(round_counter_bits[i]))

    result = bitarray()
    result += K_bit[0:60]
    result += rounding_result
    result += K_bit[65:80]

    return transform_bitarray_to_str(result[0:64]), transform_bitarray_to_str(result)


def s_box(bits):
    hex_symbol = hex(int(bits.to01(), 2)).split('0x')[1]
    hex_symbol = s_mapping.get(hex_symbol.upper())
    int_num = int(hex_symbol, 16)
    return bitarray('{0:04b}'.format(int_num))


def xor(a, b):
    result = bitarray()
    for j in range(len(a)):
        result.append(bool(a[j]) != bool(b[j]))
    return result


def split_to_blocks(bits):
    block_array = []
    for i in range(0, len(bits), 4):
        block_array.append(bits[i:(i + 4)])
    return block_array


def confuse_bits(block_array):
    result = bitarray()
    for i in range(4):
        for block in block_array:
            result.append(block[i])
    return result


def encrypt_round(data, key_register, round_number):
    data_bits = transform_str_to_bitarray(data)
    round_key_bits = transform_str_to_bitarray(key_register)
    data_bits = xor(data_bits, round_key_bits)
    block_array = split_to_blocks(data_bits)
    for i in range(len(block_array)):
        block_array[i] = s_box(block_array[i])
    confused_data = confuse_bits(block_array)
    round_key, key_register = update_key(key_register, round_number)
    return transform_bitarray_to_str(confused_data), round_key, key_register


def s_box_mixing(state):
    state_str = str(state)
    result = ""
    for number in state_str:
        result += s_mapping.get(number)
    return result


key_register = 'BBBB55555555EEEEFFFF'
round_data =   '0000000000107142'
# s_1 = s_box_mixing(data)
# print(s_1)

last_data = None
last_key = None
for i in range(1, 32):
    round_data, round_key, key_register = encrypt_round(round_data, key_register, i)
    print("Round ", i)
    print("Data: ", round_data)
    print("Key: ", round_key)
    last_data = round_data
    last_key = round_key

print(
    transform_bitarray_to_str(xor(
        transform_str_to_bitarray(round_data),
        transform_str_to_bitarray(round_key)
    ))
)