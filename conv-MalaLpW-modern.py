#!/usr/bin/env python3

import sys, re
from argparse import ArgumentParser

# =========================================================================
# The program implements a mechanical conversion from Schlachter's (1958)
# dictionary orthography to Ume Saami current orthography (2016, dictionary
# Barruk 2018). Some imperfections may occur, e.g. concerning vowels.
# Note that Schlachter's work and the idiolect it is based on contain some
# idiosyncracies as well.
# 
# Schlachter does not distinguish ï from i. The distinction in the current
# orthography is for the most part redundant, so in principle a lot of cases
# could be deduced (ï /_{a,á,uo}, but undecidable before {ij,uv} cf.
# jillijmus ’västligast’ - jïllijmus ’högst’). Barruk's đ ~ r is represented
# by d in Schlachter and thus undifferentiable from "normal" d.
#
# Overlong geminates are marked with /'/, e.g. beäg'ga ’storm’.
# Distinction between long (open) /å/ and short (closed) /o/, which is not
# marked in the standard orthography, can optionally be retained, see Usage.
#
# Author: Juha Kuokkala (juha.kuokkala@helsinki.fi) 2019-2020
# =========================================================================
# USAGE:
#
# Reads the first column of input line (until TAB) and adds the converted
# string as a new column in the beginning of the output line.
# (TODO: Selection of column to convert; full-text conversion)
#
# Options:
#  -G   Disable overlong geminate marking with /'/
#  -o   Distinguish short /o/ from long /å/ (default: output both as /å/)
#
# =========================================================================
# The conversion implements the following replacement rules:
#
# First syllable vowels:
#
# Vi > Vj
# Vì > Vjˈ
# Vu > Vv
# Vù > Vvˈ
# uy > uj (kuyˈna > kujnna, muyhteet > mujttiet) (ja üy? güỳvat > güjvvet)
# Vy > Vv
# V[uy]f > Vvh (> Vv[kpt] / _[kpt])
#
# aa à > á
# åå å̀ > å
# ä ä̀ > eä normally (NB. konsonant centre must be marked overlong after ä,ä̀), except
# - ä̀ is handled as ää before Schl. a/i (representing Proto-Saami *ā before *i(j))
# - ä̀ > e before Schl. e (?)
# ää > ä
# ee > e  (occurs seldom)
# ii ì > ij
# uu ù > uv
# üü ǜ > üv
# oo ò > uv (only in words with uvda-root)
#
# ia > iä
# üe > uö
# yö > uö / before ee/ie
# ö > yö (öy,öỳ > yöj ? in some words? Note still syöydee > suövđđie)
#
# eä̀ > eä (a general default rule: remove half-length marks)
#
# eä,ie > iä / before non-overlong consonantism + a/á/uo (NB. Schl. eäh[kpt] seems usually(/always?) to be eähCC in Barruk)
#
# Second syllable vowels:
#
# aa à > á
# ee è > ie
# oo ò > uo
#
# a > i /_j  (alkkije = alˈhkaja 'leicht') (also in odd final syllable?)
# a > e, when 1st-syllable vowel is {e,ä,ü} (or palatal i, but cannot be distinguished from ï in Schlachter's material)
#
# Third syllable, if word-final:
#
# a > e
#
# Normalize final-syllable ü > u, vrt. bijìmüs etc.?
#
# Consonants, generally:
#
# w > v
# ʿ[kpt] > [kpt]
# ʿ > h (muutoin)
# dhk > ŧkk
# h[gbd] > h[kpt]
# dh > ŧ
# (? ʿv > ff, vrt. tjàrʿvoo = tjárffuo [Aikio 2009]. Note though: MalåLpW darˈfee ~ darhvee; laahvès = láfies [Barruk])
#
# Between 1st and 2nd syllable:
#
# XˈZ > XZZ (simply remove from 3-consonant clusters)
# vhC > vCC , C = {kpt}
# jhC > jCC , C = {kpt}
# lhC > lCC , C = {kpt}
# rhC > rCC , C = {kpt}
# llC > lCC , C = {kptgbd}
# rrC > rCC , C = {kptgbd}
# mmb > mbb
# mmp > mpp
# nnd > ndd
# nnt > ntt
# ŋŋg > ŋgg
# ŋŋk > ŋkk
# (ssC is the same in Barruk)
#
# NB! Generalization in the Ume Saami consonant gradation pattern requires to write after short syllable: hk hp ht htj hts -> hkk hpp htt httj htts
#
# Between 2nd and 3rd syllable:
#
# hk > k
# ht > t
# hp > p ?
#
# Word initially (at least?):
# ŋj > nj
# (gŋj > gŋ or dnj; both can be found in Barruk? Rarely also gŋj)
# ŋj > ŋ  probably generally yields the best results, cf. vuaiŋjaladtja etc.
#
# Word-finally:
# g > k
# ht > t, except in initial syllable
#
# Special cases:
#
# supts > subts
#
# =========================================================================

def convert_ume(word, short_o=False, no_overlong=False):
    if re.match(r'\s*$', word):
        return word
    capit = False
    if word[0].isupper():
        capit = True
        word = word.lower()
    
    make_strong = ''
    overlong_mark = "" if no_overlong else "'"
    
    cons = 'bdđfghjklmnŋprstŧvʿˈ'
    #consS = 'bdđfghjklmnŋprstŧvʿˈiuyìùỳ'  # incl. Schlachter's semivowel letters which mark consonants
    consC = '[iuyìùỳ'+ cons +']*['+ cons +']+'  # cons.center, may begin with Schlachter's semivowel letters
    
    word = re.sub(r'ia', 'iä', word)  # normalize some occasional variants
    word = re.sub(r'uä', 'ua', word)
    word = re.sub(r'üe|üä', 'uö', word)
    word = re.sub(r'äa', 'eä', word)
    
    word = re.sub(r'aa|à', 'á', word)
    word = re.sub(r'åå|å̀', r'@OO@', word)
    word = word.replace('å', 'o')  # keep short o distinct from long one at least during later processing
    word = word.replace('@OO@', 'å')
    
    m = re.match('[' +cons+ r']*eä[^̀]', word)  # imterim empirical rule: after Schl. short eä always B. strong hkk etc.
    if m:
        make_strong = 'obstr'
    word = re.sub(r'ä̀(?=' +consC+ r'e([^e]|$))', 'e', word)
    word = re.sub(r'ä̀(?=' +consC+ r'[ai])', 'ää', word)
    m = re.match(r'(.*)((?<![eiä])ä(?=[^ä])|ä̀)('+ consC +r')(.*)', word)  # ä̀ or single ä, which is not part of eä/iä/ää sequence (nor word-final)
    if m:
        cc = m.group(3)
        if re.match(r'h(k|p|t[js]?)$', cc):
            make_strong = 'obstr'     # mark later with strongest grade
        else:
            cc = re.sub(r'^(.+)(.)$', r'\1ˈ\2', cc)  # mark strongest grade now
        word = m.group(1) + 'eä' + cc + m.group(4)
    word = re.sub(r'ää', 'ä', word)
    
    word = word.replace('ìu','iv').replace('ùi','uj') 
    word = re.sub(r'(?<![aeiouyäáåöü])ì|ii', 'ij', word)
    word = re.sub(r'(?<![aeiouyäáåöü])ù|uu', 'uv', word)
    word = re.sub(r'üü|ǜ', 'üv', word)
    word = re.sub(r'^([' +cons+ r']*)ee', r'\1e', word)  # only in 1st syllable
    word = re.sub(r'ee|i?è', 'ie', word)
    word = re.sub(r'^([' +cons+ r']*)(oo|ò)', r'\1uv', word)  # only in 1st syllable
    word = re.sub(r'oo|u?ò', 'uo', word)
    word = re.sub(r'yö(?=[^aeoäáåöü]+ie)', 'uö', word)
    word = re.sub(r'(?<![uy])ö', 'yö', word)
    #word = re.sub(r'yöy', 'yöi', word)
    #word = re.sub(r'yöỳ', 'yöì', word)
    word = word.replace(r'̀', '') # remove remaining half-long marks (eä̀, yö̀)

    word = re.sub(r'([aeouyäáåöü])i', r'\1j', word)
    word = re.sub(r'([aeouyäáåöü])ì', r'\1jˈ', word)  # length of syllable-final semivowel indicates strong grade
    word = re.sub(r'([uü])y', r'\1j', word)
    word = re.sub(r'([uü])ỳ', r'\1jˈ', word)
    word = re.sub(r'([aeiouyäáåöü])(ù|ỳ)', r'\1vˈ', word)
    word = re.sub(r'([aeiouyäáåöü])(uf|yf)', r'\1vh', word)
    word = re.sub(r'([aeiouyäáåöü])[uy]', r'\1v', word)
    
    word = re.sub(r'w', 'v', word)
    word = re.sub(r'ʿ([kpt])', r'\1', word)
    word = re.sub(r'ʿ', 'h', word)
    word = word.replace('dhk', 'ŧkk')
    word = word.replace('hg', 'hk').replace('hb', 'hp').replace('hd', 'ht')
    word = word.replace('dh', 'ŧ')
    word = re.sub(r'^ŋj', 'nj', word)
    word = re.sub(r'ŋj', 'ŋ', word)
    word = re.sub(r'g$', 'k', word)
    word = re.sub(r'supts', 'subts', word)  # special case?
    
    # 'dadnie' --> 'd', 'a', 'dn', 'ie'
    consvoc = re.split(r'(ie|iä|eä|ua|uo|uä|uö|ue|yö|a|e|i|o|u|ü|y|å|ä|á|ï|’)', word)
    #print(repr(consvoc)) ###
    #print(repr(consvoc) + " / make_strong = '%s'" %(make_strong)) ###

    for i in range(3, len(consvoc), 4):  # stressed eä,ie > iä / before non-overlong consonantism + a/á/uo
        if consvoc[i-2] in ('eä','ie') and consvoc[i] in ('a','á','uo'):
            if not (make_strong or re.match(r'(?:.*ˈ|(.)\1.|.(.)\2|.h.|[kptgbd]{2}[js])', consvoc[i-1])):
                consvoc[i-2] = 'iä'

    for i in range(2, len(consvoc), 4):  # conconant centre after odd-numbered syllable
        consvoc[i] = consvoc[i].replace('ˈˈ', 'ˈ')  # possible superfluous strong grade signs from previous operations
        consvoc[i] = re.sub(r'^(.)ˈ\1$', r'\1' + overlong_mark + r'\1', consvoc[i])    # XˈX > X'X
        consvoc[i] = re.sub(r'^(s)ˈ([^s])', r'\1\1\2', consvoc[i])  # sˈZ > ssZ
        consvoc[i] = re.sub(r'^(.)ˈ(.)(j?)$', r'\1\2\2\3', consvoc[i])  # XˈZ > XZZ (Z may also be Cj)
        consvoc[i] = re.sub(r'ˈ', r'', consvoc[i])                      # XZˈQ > XZQ
        consvoc[i] = re.sub(r'([lrjv])h([kpt])', r'\1\2\2', consvoc[i])   # LhC > LCC , C = {kpt}
        consvoc[i] = re.sub(r'([lr])\1([kptgbd])', r'\1\2\2', consvoc[i])   # LLC > LCC , C = {kptgbd}
        consvoc[i] = re.sub(r'([mnŋ])\1([kptgbd])', r'\1\2\2', consvoc[i])  # mmb > mbb etc.
        if re.match(r'h(k|p|t[js]?)$', consvoc[i]) and len(consvoc) > i+1 and (make_strong or re.match(r'[aeiouüy]$', consvoc[i-1])):
            consvoc[i] = re.sub(r'([kpt])', r'\1\1', consvoc[i])  # after short syllable, always strong grade geminated obstruent: ht > htt, htj > httj etc.
    for i in range(4, len(consvoc), 4):  # conconant centre after even-numbered syllable
        consvoc[i] = re.sub(r'h([kpt])', r'\1', consvoc[i])
    for i in range(3, len(consvoc), 4):  # vowels in even-numbered syllable
        if consvoc[i] == 'a' and len(consvoc) > i+2 and consvoc[i+1].startswith('j'):
            consvoc[i] = 'i'
        elif consvoc[i] == 'a' and consvoc[i-2] in 'äüe':
            consvoc[i] = 'e'
    for i in range(5, len(consvoc), 4):  # vowels in odd-numbered, non-first syllable
        if i+1 <= len(consvoc) <= i+2:  # if word-final syllable:
            if consvoc[i] == 'a':
                consvoc[i] = 'e'
            elif consvoc[i] == 'ü':
                consvoc[i] = 'u'
    if len(consvoc) > 3 and consvoc[-1] == 'ht':  # final ht > t, if not in 1st syllable
        consvoc[-1] = 't'
    word = ''.join(consvoc)
    
    word = word.replace('bmm','bm').replace('dnn','dn').replace('gŋŋ','gŋ')
    word = word.replace('vvv',"v'v")
    word = re.sub(r'(átj|[dt]all|[uü]vv)et', r'\1at', word)  # compensate for syncope side effects
    if not short_o:
        word = re.sub(r'(^|[^u])o', r'\1å', word)  # change short o to standard orthography å
    
    if capit:
        word = word.capitalize()
    
    return word

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def main():
    ap = ArgumentParser(description='Mechanical conversion from Schlachter\'s (1958) ' \
                        'dictionary orthography to Ume Saami current orthography (2016). ' \
                        ' - The running text mode (default) converts whole input lines and ' \
                        'outputs the converted lines. The --field mode reads a single ' \
                        '(TAB-separated) column from the input line and adds the converted ' \
                        'string as a new column in the beginning of the output line.')
    ap.add_argument('-f', '--field', type=int, metavar='N', nargs="?", const=1,
                        help='Convert only given field (column) and insert the result to the beginning of line. ' \
                             '-f without N uses the first field.')
    ap.add_argument('-G', '--no_overlong', action='store_true', default=False,
                        help='Disable overlong geminate marking with /\'/')
    ap.add_argument('-o', '--short_o', action='store_true', default=False,
                        help='Distinguish short /o/ from long /å/ (default: output both as /å/)')
    opts = ap.parse_args()

    for line in sys.stdin:
        if opts.field:
            fields = line.rstrip('\r\n').split('\t')
            orig = fields[opts.field -1].replace('\r', '').replace('\n', '')
        else:
            orig = line
        
        orig = re.sub(r'(vuahta|gååhteet)$', r'|\1', orig)  # special compound-like suffixes, separate with '|'
        
        parts = re.split(r'([|_ -]+)', orig)  # get both the elements and the separators (whitespace & hyphens &c.)
        for i in range(len(parts)):
            parts[i] = convert_ume(parts[i], opts.short_o, opts.no_overlong)
        
        if opts.field:
            line = ''.join(parts).replace('|','') + '\t' + line
        else:
            line = ''.join(parts).replace('|','')
        sys.stdout.write(line)

if __name__ == '__main__':
    main()
