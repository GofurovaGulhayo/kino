from django.shortcuts import render
from .utils.monoalphabetic.caesar import encrypt_caesar, decrypt_caesar
from .utils.monoalphabetic.bacon import encrypt_bacon, decrypt_bacon
from .utils.monoalphabetic.atbash import solve_atbash


def cypher_main(request):
    return render(request, 'cypher/main.html')


def caesar(request):
    if request.method == 'POST':
        caesarList = False
        decrypt = False

        if request.POST['cipherEncrypt'] == 'False':
            decrypt = True
            ciphertext = request.POST['ciphertext']
            shift = request.POST.get('shift', False)

            if shift:
                shift = int(shift)
                plaintext = decrypt_caesar(ciphertext, shift=shift)
            else:
                caesarList = True
                plaintext = decrypt_caesar(ciphertext)
        else:
            plaintext = request.POST['plaintext']
            shift = int(request.POST['shift'])
            ciphertext = encrypt_caesar(plaintext, shift)

        return render(request, 'cypher/caesar.html', {'plaintext': plaintext, 'shift': shift,
                                                      'ciphertext': ciphertext, 'caesarList': caesarList,
                                                      'decrypt': decrypt})

    return render(request, 'cypher/caesar.html')


def atbash(request):
    if request.method == 'POST':
        decrypt = False

        if request.POST['cipherEncrypt'] == 'False':
            decrypt = True

            ciphertext = request.POST['ciphertext']
            plaintext = solve_atbash(ciphertext)
        else:
            plaintext = request.POST['plaintext']
            ciphertext = solve_atbash(plaintext)

        return render(request, 'cypher/atbash.html', {'plaintext': plaintext, 'ciphertext': ciphertext,
                                                      'decrypt': decrypt})

    return render(request, 'cypher/atbash.html')


def rot13(request):
    if request.method == 'POST':
        decrypt = False

        if request.POST['cipherEncrypt'] == 'False':
            decrypt = True

            ciphertext = request.POST['ciphertext']
            plaintext = decrypt_caesar(ciphertext, shift=13)
        else:
            plaintext = request.POST['plaintext']
            ciphertext = encrypt_caesar(plaintext, shift=13)

        return render(request, 'cypher/rot13.html', {'plaintext': plaintext, 'ciphertext': ciphertext,
                                                     'decrypt': decrypt})

    return render(request, 'cypher/rot13.html')


def bacon(request):
    if request.method == 'POST':
        decrypt = False
        origin_table = request.POST.get('originalTable', False)

        if request.POST['cipherEncrypt'] == 'False':
            decrypt = True
            ciphertext = request.POST['ciphertext']

            if origin_table:
                plaintext = decrypt_bacon(ciphertext)
            else:
                plaintext = decrypt_bacon(ciphertext, original=False)
        else:
            plaintext = request.POST['plaintext']

            if origin_table:
                ciphertext = encrypt_bacon(plaintext)
            else:
                ciphertext = encrypt_bacon(plaintext, original=False)

        return render(request, 'cypher/bacon.html', {'plaintext': plaintext, 'ciphertext': ciphertext,
                                                     'decrypt': decrypt, 'originTable': origin_table})

    return render(request, 'cypher/bacon.html')
