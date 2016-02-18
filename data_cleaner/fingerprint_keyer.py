#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
import unicodedata

#For the translate make a dictionary and do replaces based on the difference 
#of chars
#=============================================================================

def strip_accents(s):
    if type(s) == str :
        s = unicode(s, "utf-8")
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def FingerprintKeyer(key_string):
    #assert type(key_string) == str,"ERROR: key must be a string."
    #assert type(key_string) == str,"ERROR: key must be a string."
    if type(key_string) != str :
        key_string = key_string.encode('utf8')
    
    #remove leading and trailing whitespace
    key_string = key_string.strip().lower()
    
    #change all characters to their lower case representation
    key_string = key_string.lower()
    
    #remove all punctuation and control characters
    for punct in (set(key_string) & set(string.punctuation)):
        key_string = key_string.replace(punct,"")
    
    key_string = key_string.replace("\t", " ")
    
    #split the string into whitespace-separated tokens
    split_key = key_string.split()
    
    #sort the tokens and remove duplicates
    unique_sorted_split_key = sorted(set(split_key))
    
    #join the tokens back together
    finger_printed_key = " ".join(unique_sorted_split_key)
    
    #normalize extended western characters to their ASCII 
    #representation (for example "gödel" → "godel")
    finger_printed_key = strip_accents(finger_printed_key)
    return finger_printed_key


def GroupFingerprintStrings(inp) :
    """
    Retorna un diccionario donde las keys son los fingerprints y los valores las strings originales
    Tambien retorna un conteo de las strings originales
    """
    res = {}
    counts = {}
    for (k,s) in zip(map(FingerprintKeyer, inp), inp) :
        res[k] = res.get(k, []) + [s]
        counts[s] = counts.get(s, 0) + 1
    return res, counts

def GetBestReplacements(d, counts) :
    """
    Itera por cada cluster para determinar la mejor string para reemplazar las strings originales
    De momento solo utiliza un conteo simple pero podria agregarse algun criterio basado en la capitalizacion de las palabras
    """
    res = {}
    for (k,v) in d.items() :
        res[k] = max(v, key=lambda s: counts[s])
    return res
    
def ReplaceByKey(d, l) :
    return [d.get(FingerprintKeyer(s), s) for s in l]

