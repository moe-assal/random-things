from math import floor
"""
Crypto Class v1.0
done by:
    Moe Assal
Contact:
    mohammad.elassal04@gmail.com
    phone number: +96171804948
    location: Lebanon, Bekaa, Khirbet Rouha
"""


class Crypto:
    def __init__(self):
        pass

    def shift(self, string: str, shift_num: int) -> str:
        """
        :param shift_num:
            can be passed as a negative int or a positive one.
        :return:
            shifts the string characters by shift_num
        """
        encrypted = ""
        for letter in string:
            if letter in ["\t", "\n", "\0"]:
                encrypted += letter
                continue
            encrypted += chr(ord(str(letter)) + shift_num)
        return encrypted

    def pass_shift(self, string: str, passw: str, dec: bool = False) -> str:
        """
        :param string:
            string passed to be encrypted or decrypted
        :param passw:
            password that encrypts or decrypts the "string"
        :param dec:
            if set to True, then you want to decrypt, else it will encrypt.
        :return:
            returns the encrypted or decrypted string
        """
        encrypted = ""
        i = 0
        if not dec:
            for letter in string:
                encrypted += self.shift(letter, ord(str(passw[i])))
                i += 1
                i %= len(passw)
        else:
            for letter in string:
                encrypted += self.shift(letter, - ord(str(passw[i])))
                i += 1
                i %= len(passw)
        return encrypted

    def column_enc(self, string, col, times=None):
        def static_column_enc(__string__, __col__):
            assert __col__ != 0
            encrypted = ""
            for start in range(__col__):
                for increment in range(start, len(__string__), __col__):
                    encrypted += __string__[increment]
            return encrypted
        if isinstance(col, list):
            if times is None:
                times = len(col)
            for time in range(times):
                string = static_column_enc(string, col[time % len(col)])
        else:
            string = static_column_enc(string, col)
        return string

    def column_dec(self, string, cols):
        def static_column_dec(__string__, __col__):
            """
            :var indexes:
                stores the indexes of the characters that must be removed
            :var step:
                defines the step in the decryption that must be token
                example:
                    :param __string__ = "hore llwdlo"
                    :param __col__ = 4
                    hore llwdlo
                    ^12^12^12^12..
                    :var encrypted = "hell"
                    then remove the added characters to encrypted, decrement :var step and we are left with:
                    or lwdo
                    ^1^1^1^1..
                    :var encrypted = "hello wo"
                    rld
                    ^^^
                    :var encrypted = "hello world"

            :return encrypted

            """
            assert __col__ != 0
            encrypted = ""
            indexes = []
            while len(__string__) != 0:
                indexes.clear()
                step = int(floor(len(__string__) / __col__))
                error = len(__string__) % __col__
                character_index = 0
                while True:
                    if character_index not in range(0, len(__string__)) or step == 0:
                        break
                    if error != 0 and character_index != 0:
                        character_index += 1
                        error -= 1
                    encrypted += __string__[character_index]
                    indexes.append(character_index)
                    character_index += step
                if indexes.__len__() == 0:
                    return encrypted + __string__
                __string__ = self.remove_indexes(__string__, indexes)
            return encrypted
        if isinstance(cols, list):
            cols.reverse()
            for col in cols:
                string = static_column_dec(string, col)
            return string
        else:
            return static_column_dec(string, cols)

    def column_cryptography(self, string: str, cols):
        """
        :param string:
            string to be encrypted or decrypted
        :param cols:
            Passed as an integer or a list of integers. A negative integer will decrypt and a positive one will encrypt.
        :return:
            Column decryption:
                string = "hello world"
                cols = 4
                h e l l
                o   w o
                r l d
                :return = hore llwdlo
                    cols is the width of the matrix. the matrix writes the letters horizontally. the encrypted word is
                    taken from the vertical addition of the letters of the matrix.
                string = "hore llwdlo"
                cols = -4
                :return = hello world

        """
        if isinstance(cols, list):
            for col in cols:
                if col < 0:
                    string = self.column_dec(string, abs(col))
                else:
                    string = self.column_enc(string, col)
        else:
            if cols < 0:
                string = self.column_dec(string, abs(cols))
            else:
                string = self.column_enc(string, cols)
        return string

    def remove(self, string, index) -> str:
        assert len(string) >= index >= 0
        return string[0:index] + string[index + 1:]

    def remove_indexes(self, string, indexes) -> str:
        indexes.sort()
        indexes.reverse()
        for index in indexes:
            string = self.remove(string, index)
        return string


deh = Crypto()
print(deh.shift("""jgsKc	jgs^ccrPNOW
m}l	OPQR
PNOW	l
k	PNOW
qlS	NN
__n	OQSUW
>P	l
i_x_KSe	UVNUTPUVVV
	UTUR""", -30))
