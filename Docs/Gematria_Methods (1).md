# Gematria Methods Reference

This document summarizes the core gematria methods for Hebrew, Greek, English (TQ), and Coptic systems. These methods form the base set for the initial release of the Advanced Gematria App.

---

## Hebrew Gematria Methods

### Hebrew Alphabet Values

| Letter | Name | Value |
| :---- | :---- | :---- |
| א | Aleph | 1 |
| ב | Bet | 2 |
| ג | Gimel | 3 |
| ד | Dalet | 4 |
| ה | He | 5 |
| ו | Vav | 6 |
| ז | Zayin | 7 |
| ח | Chet | 8 |
| ט | Tet | 9 |
| י | Yod | 10 |
| כ/ך | Kaf/Final Kaf | 20/500 |
| ל | Lamed | 30 |
| מ/ם | Mem/Final Mem | 40/600 |
| נ/ן | Nun/Final Nun | 50/700 |
| ס | Samekh | 60 |
| ע | Ayin | 70 |
| פ/ף | Pe/Final Pe | 80/800 |
| צ/ץ | Tsadi/Final Tsadi | 90/900 |
| ק | Qof | 100 |
| ר | Resh | 200 |
| ש | Shin | 300 |
| ת | Tav | 400 |

*Final letter values are used in some specific methods only*

### Method Categories

#### 1\. Basic Value Methods

- **Standard Value (מספר הכרחי, Mispar Hechrachi):** Assigns standard values to each letter.  
    
  - *Example:* יהוה \= י(10) \+ ה(5) \+ ו(6) \+ ה(5) \= 26


- **Ordinal Value (מספר סידורי, Mispar Siduri):** Based on letter position (1–22).  
    
  - *Example:* יהוה \= י(10th letter \= 10\) \+ ה(5th letter \= 5\) \+ ו(6th letter \= 6\) \+ ה(5th letter \= 5\) \= 26


- **Final Letter Values (מספר סופית, Mispar Sofit):** Uses special values for final forms.  
    
  - *Example:* מלך \= מ(40) \+ ל(30) \+ ך(final kaf \= 500\) \= 570  
  - *Compared to standard:* מלך \= מ(40) \+ ל(30) \+ כ(20) \= 90

#### 2\. Reduction Methods

- **Small/Reduced Value (מספר קטן, Mispar Katan):** Reduces values to a single digit.  
    
  - *Example:* אדם \= א(1) \+ ד(4) \+ ם(40→4) \= 9  
  - *Note:* Values above 9 are reduced to a single digit (e.g., 40→4, 400→4)


- **Integral Reduced Value (מספר מספרי, Mispar Mispari):** Sums the digits of each letter's value.  
    
  - *Example:* שלום \= ש(300→3+0+0=3) \+ ל(30→3+0=3) \+ ו(6) \+ ם(40→4+0=4) \= 16


- **Integral Reduced Ordinal Value (מספר קטן מספרי, Mispar Katan Mispari):** Reduces ordinal value to a single digit.  
    
  - *Example:* אבג \= א(1st letter \= 1\) \+ ב(2nd letter \= 2\) \+ ג(3rd letter \= 3\) \= 6

#### 3\. Mathematical Operations

- **Square Value (מספר בונה, Mispar Bone'eh):** Squares each letter's value.  
    
  - *Example:* אב \= א(1²=1) \+ ב(2²=4) \= 5


- **Cubed Value (מספר משולש, Mispar Meshulash):** Cubes each letter's value.  
    
  - *Example:* אב \= א(1³=1) \+ ב(2³=8) \= 9


- **Triangular Value (מספר קדמי, Mispar Kidmi):** Uses triangular numbers for each letter.  
    
  - *Example:* אב \= א(triangular of 1 \= 1\) \+ ב(triangular of 2 \= 3\) \= 4  
  - *Note:* Triangular number of n \= n(n+1)/2


- **Full Square Value (מספר המרובע הכללי, Mispar HaMerubah HaKlali):** Sum of squares of each letter's value.  
    
  - *Example:* אבג \= א(1²) \+ ב(2²) \+ ג(3²) \= 1 \+ 4 \+ 9 \= 14


- **Ordinal Building Value (מספר בונה סידורי, Mispar Boneah Siduri):** Squares ordinal values.  
    
  - *Example:* אבג \= א(1st letter, 1²=1) \+ ב(2nd letter, 2²=4) \+ ג(3rd letter, 3²=9) \= 14

#### 4\. Full Spelling Methods

- **Full Value (מספר גדול, Mispar Gadol):** Sums values of spelled-out letter names.  
    
  - *Example:* א \= אלף \= א(1) \+ ל(30) \+ פ(80) \= 111  
  - *Example word:* אב \= אלף(111) \+ בית(412) \= 523


- **Full Value with Finals (מספר גדול סופית, Mispar Gadol Sofit):** Sums values of spelled-out letter names, using final letter values where applicable.  
    
  - *Example:* א \= אלף \= א(1) \+ ל(30) \+ ף(final pe \= 800\) \= 831  
  - *Example word:* אב \= אלף(831) \+ בית(412) \= 1243


- **Name Value (מספר שמי, Mispar Shemi):** Multiplies values of spelled-out letter names.  
    
  - *Example:* אב \= אלף(111) × בית(412) \= 45,732


- **Name Value with Finals (מספר שמי סופית, Mispar Shemi Sofit):** Multiplies values of spelled-out letter names, using final letter values where applicable.  
    
  - *Example:* אב \= אלף(831) × בית(412) \= 342,372


- **Hidden Value (מספר נעלם, Mispar Ne'elam):** Value of letter name minus the letter itself.  
    
  - *Example:* א \= אלף \- א \= (111) \- 1 \= 110  
  - *Example word:* אב \= (אלף-א) \+ (בית-ב) \= 110 \+ 410 \= 520


- **Hidden Value with Finals (מספר נעלם סופית, Mispar Ne'elam Sofit):** Value of letter name using final letter values where applicable, minus the letter itself.  
    
  - *Example:* א \= אלף \- א \= (831) \- 1 \= 830  
  - *Example word:* אך \= (אלף-א) \+ (כף-כ) \= 830 \+ 800 \= 1630


- **Face Value (מספר הפנים, Mispar HaPanim):** Full value of the first letter as it is spelled, plus the standard values of the remaining letters.  
    
  - *Example word:* אב \= אלף(111) \+ ב(2) \= 113  
  - *Example word:* אבאה \= אלף(111) \+ ב(2) \+ א(1) \+ ה(5) \= 119  
  - *Example with letter name:* בית (the name of letter Beth) \= בית(412) \+ י(10) \+ ת(400) \= 822


- **Face Value with Finals (מספר הפנים סופית, Mispar HaPanim Sofit):** Full value of the first letter as it is spelled using final letter values where applicable, plus the standard values of the remaining letters.  
    
  - *Example word:* אב \= אלף(831) \+ ב(2) \= 833  
  - *Example word:* כב \= כף(820) \+ ב(2) \= 822


- **Back Value (מספר האחור, Mispar HaAchor):** Standard values of all letters except the last, plus the full value of the last letter as it is spelled.  
    
  - *Example word:* אב \= א(1) \+ בית(412) \= 413  
  - *Example word:* אבאה \= א(1) \+ ב(2) \+ א(1) \+ הא(6) \= 10  
  - *Example with letter name:* בית (the name of letter Beth) \= ב(2) \+ י(10) \+ תו(406) \= 418


- **Back Value with Finals (מספר האחור סופית, Mispar HaAchor Sofit):** Standard values of all letters except the last, plus the full value of the last letter as it is spelled using final letter values where applicable.  
    
  - *Example word:* אף \= א(1) \+ פא(81) \= 82  
  - *Example word:* אך \= א(1) \+ כף(820) \= 821

#### 5\. Collective Methods

- **Collective Value (מספר כולל, Mispar Kolel):** Standard value plus number of letters.  
    
  - *Example:* תורה \= ת(400) \+ ו(6) \+ ר(200) \+ ה(5) \= 611 \+ 4 letters \= 615


- **Name Collective Value (מספר שמי כולל, Mispar Shemi Kolel):** Name value plus number of letters.  
    
  - *Example:* אב \= אלף(111) \+ בית(412) \= 523 \+ 2 letters \= 525


- **Name Collective Value with Finals (מספר שמי כולל סופית, Mispar Shemi Kolel Sofit):** Name value using final letter values where applicable, plus number of letters.  
    
  - *Example:* אב \= אלף(831) \+ בית(412) \= 1243 \+ 2 letters \= 1245  
  - *Example:* אך \= אלף(831) \+ כף(820) \= 1651 \+ 2 letters \= 1653


- **Regular plus Collective (רגיל פלוס כולל, Ragil plus Kolel):** Standard value plus \+ 1\.  
    
  - *Example:* תורה \= ת(400) \+ ו(6) \+ ר(200) \+ ה(5) \= 611 \+ 1 \= 612

#### 6\. Substitution Methods

- **AtBash (את בש):** Reverse substitution cipher.  
    
  - *Example:* אבג → תשר \= ת(400) \+ ש(300) \+ ר(200) \= 900  
  - *Note:* א is replaced with ת, ב with ש, ג with ר, etc.


- **Albam (אלבם):** Letter pairing substitution.  
    
  - *Example:* אבג → כלמ \= כ(20) \+ ל(30) \+ מ(40) \= 90  
  - *Note:* א is replaced with כ, ב with ל, ג with מ, etc.

---

## Greek Isopsephy Methods

### Greek Alphabet Values

| Letter | Name | Value |
| :---- | :---- | :---- |
| Α α | Alpha | 1 |
| Β β | Beta | 2 |
| Γ γ | Gamma | 3 |
| Δ δ | Delta | 4 |
| Ε ε | Epsilon | 5 |
| Ϝ ϝ | Digamma | 6 |
| Ζ ζ | Zeta | 7 |
| Η η | Eta | 8 |
| Θ θ | Theta | 9 |
| Ι ι | Iota | 10 |
| Κ κ | Kappa | 20 |
| Λ λ | Lambda | 30 |
| Μ μ | Mu | 40 |
| Ν ν | Nu | 50 |
| Ξ ξ | Xi | 60 |
| Ο ο | Omicron | 70 |
| Π π | Pi | 80 |
| Ϙ ϙ | Koppa | 90 |
| Ρ ρ | Rho | 100 |
| Σ σ/ς | Sigma | 200 |
| Τ τ | Tau | 300 |
| Υ υ | Upsilon | 400 |
| Φ φ | Phi | 500 |
| Χ χ | Chi | 600 |
| Ψ ψ | Psi | 700 |
| Ω ω | Omega | 800 |
| ϡ | Sampi | 900 |

*Digamma, Koppa, and Sampi are archaic letters used for numbers only*

### Method Categories

#### 1\. Basic Value Methods

- **Standard Value (Αριθμός Κανονικός, Arithmos Kanonikos):** Assigns standard values to each letter.  
    
  - *Example:* Λόγος \= Λ(30) \+ ό(70) \+ γ(3) \+ ο(70) \+ ς(200) \= 373


- **Ordinal Value (Αριθμός Τακτικός, Arithmos Taktikos):** Based on letter position (1–24).  
    
  - *Example:* Λόγος \= Λ(11th letter \= 11\) \+ ό(15th letter \= 15\) \+ γ(3rd letter \= 3\) \+ ο(15th letter \= 15\) \+ ς(18th letter \= 18\) \= 62

#### 2\. Reduction Methods

- **Small Value (Αριθμός Μικρός, Arithmos Mikros):** Reduces values to a single digit.  
    
  - *Example:* Λόγος \= Λ(30→3) \+ ό(70→7) \+ γ(3) \+ ο(70→7) \+ ς(200→2) \= 22→4  
  - *Note:* Values are reduced to a single digit (e.g., 30→3, 200→2)


- **Digital Value (Αριθμός Ψηφιακός, Arithmos Psephiakos):** Sums the digits of each letter's value.  
    
  - *Example:* Λόγος \= Λ(30→3+0=3) \+ ό(70→7+0=7) \+ γ(3) \+ ο(70→7+0=7) \+ ς(200→2+0+0=2) \= 22


- **Digital Ordinal Value (Αριθμός Τακτικός Ψηφιακός, Arithmos Taktikos Psephiakos):** Reduces ordinal value to a single digit.  
    
  - *Example:* Λόγος \= Λ(11→1+1=2) \+ ό(15→1+5=6) \+ γ(3) \+ ο(15→1+5=6) \+ ς(18→1+8=9) \= 26

#### 3\. Mathematical Operations

- **Square Value (Αριθμός Τετράγωνος, Arithmos Tetragonos):** Squares each letter's value.  
    
  - *Example:* Θεός \= Θ(9²=81) \+ ε(5²=25) \+ ό(70²=4900) \+ ς(200²=40000) \= 45006


- **Cubic Value (Αριθμός Κύβος, Arithmos Kyvos):** Cubes each letter's value.  
    
  - *Example:* Θεός \= Θ(9³=729) \+ ε(5³=125) \+ ό(70³=343000) \+ ς(200³=8000000) \= 8343854


- **Triangular Value (Αριθμός Τριγωνικός, Arithmos Trigonikos):** Uses triangular numbers for each letter.  
    
  - *Example:* Θεός \= Θ(triangular of 9 \= 45\) \+ ε(triangular of 5 \= 15\) \+ ό(triangular of 70 \= 2485\) \+ ς(triangular of 200 \= 20100\) \= 22645  
  - *Note:* Triangular number of n \= n(n+1)/2


- **Ordinal Square Value (Αριθμός Τακτικός Τετράγωνος, Arithmos Taktikos Tetragonos):** Squares ordinal values.  
    
  - *Example:* Θεός \= Θ(9th letter, 9²=81) \+ ε(5th letter, 5²=25) \+ ό(15th letter, 15²=225) \+ ς(18th letter, 18²=324) \= 655

#### 4\. Full Spelling Methods

- **Full Value (Αριθμός Πλήρης, Arithmos Pleres):** Sums values of spelled-out letter names.  
    
  - *Example:* α \= ἄλφα \= α(1) \+ λ(30) \+ φ(500) \+ α(1) \= 532  
  - *Example word:* αβ \= ἄλφα(532) \+ βῆτα(311) \= 843


- **Name Value (Αριθμός Ονοματικός, Arithmos Onomatikos):** Multiplies values of spelled-out letter names.  
    
  - *Example:* αβ \= ἄλφα(532) × βῆτα(311) \= 165,452


- **Individual Value (Αριθμός Εξατομικευμένος, Arithmos Exatomikeumenos):** Sums values of each spelled-out letter.  
    
  - *Example:* α \= ἄλφα \= α(1) \+ λ(30) \+ φ(500) \+ α(1) \= 532  
  - *Example word:* αβ \= α(532) \+ β(311) \= 843


- **Hidden Value (Αριθμός Κρυμμένος, Arithmos Krymmenos):** Value of letter name minus the letter itself.  
    
  - *Example:* α \= ἄλφα \- α \= (532) \- 1 \= 531  
  - *Example word:* αβ \= (ἄλφα-α) \+ (βῆτα-β) \= 531 \+ 309 \= 840


- **Face Value (Αριθμός Προσωπείο, Arithmos Prosopeio):** Full value of the first letter as it is spelled, plus the standard values of the remaining letters.  
    
  - *Example word:* αβ \= ἄλφα(532) \+ β(2) \= 534  
  - *Example word:* αβγα \= ἄλφα(532) \+ β(2) \+ γ(3) \+ α(1) \= 538  
  - *Example with letter name:* βῆτα (the name of letter Beta) \= βῆτα(311) \+ ῆ(8) \+ τ(300) \+ α(1) \= 620


- **Back Value (Αριθμός Οπίσθιος, Arithmos Opisthios):** Standard values of all letters except the last, plus the full value of the last letter as it is spelled.  
    
  - *Example word:* αβ \= α(1) \+ βῆτα(311) \= 312  
  - *Example word:* αβγα \= α(1) \+ β(2) \+ γ(3) \+ ἄλφα(532) \= 538  
  - *Example with letter name:* βῆτα (the name of letter Beta) \= β(2) \+ ῆ(8) \+ τ(300) \+ ἄλφα(532) \= 842

#### 5\. Collective Methods

- **Collective Value (Αριθμός Συλλογικός, Arithmos Syllogikos):** Standard value plus number of letters.  
    
  - *Example:* Ἰησοῦς \= Ἰ(10) \+ η(8) \+ σ(200) \+ ο(70) \+ ῦ(400) \+ ς(200) \= 888 \+ 6 letters \= 894


- **Name Collective Value (Αριθμός Ονοματικός Συλλογικός, Arithmos Onomatikos Syllogikos):** Name value plus number of letters.  
    
  - *Example:* αβ \= ἄλφα(532) \+ βῆτα(311) \= 843 \+ 2 letters \= 845


- **Regular plus Collective (Κανονικός Συν Συλλογικός, Kanonikos Syn Syllogikos):** Standard value plus \+1  
    
  - *Example:* Ἰησοῦς \= 888 \+ 1  \= 889

#### 6\. Substitution Methods

- **Reverse Substitution (Αντίστροφη Αντικατάσταση, Antistrōphē Antikatastasē):** Alphabet reversed.  
    
  - *Example:* αβγ → ωψχ \= ω(800) \+ ψ(700) \+ χ(600) \= 2100  
  - *Note:* α is replaced with ω, β with ψ, γ with χ, etc.


- **Pair Matching (Αντιστοίχιση Ζεύγους, Antistoichisi Zeugous):** Letter pairing substitution.  
    
  - *Example:* αβγ → λκι \= λ(30) \+ κ(20) \+ ι(10) \= 60  
  - *Note:* α is replaced with λ, β with κ, γ with ι, etc.


- **Next Letter Value (Αριθμός Επόμενος, Arithmos Epomenos):** Value of the following letter.  
    
  - *Example:* αβγ \= β(2) \+ γ(3) \+ δ(4) \= 9  
  - *Note:* Each letter is replaced with the next letter in the alphabet


- **Cyclical Permutation (Κυκλική Μετάθεση, Kyklikē Metathesē):** Cyclically permutes groups of letters.  
    
  - *Example:* αβγδ → βγδα \= β(2) \+ γ(3) \+ δ(4) \+ α(1) \= 10  
  - *Note:* Shifts all letters one position to the left

---

## English Gematria (Trigrammaton Qabbalah, TQ)

### TQ Value Table

| Letter | TQ Value | Letter | TQ Value |
| :---- | :---- | :---- | :---- |
| i, I | 0 | o, O | 10 |
| l, L | 1 | g, G | 11 |
| c, C | 2 | f, F | 12 |
| h, H | 3 | e, E | 13 |
| p, P | 4 | r, R | 14 |
| a, A | 5 | s, S | 15 |
| x, X | 6 | q, Q | 16 |
| j, J | 7 | k, K | 17 |
| w, W | 8 | y, Y | 18 |
| t, T | 9 | z, Z | 19 |
| b, B | 20 | m, M | 21 |
| v, V | 22 | d, D | 23 |
| n, N | 24 | u, U | 25 |

### Method Categories

- **Standard TQ Value:** Sum the assigned TQ values of all letters.  
    
  - *Example:* LIGHT \= L(1) \+ I(0) \+ G(11) \+ H(3) \+ T(9) \= 24


- **TQ Reduction:** Reduce the final sum to a single digit by adding the digits together.  
    
  - *Example:* LIGHT \= 24 → 2+4 \= 6  
  - *Note:* Continue adding digits until a single digit is reached


- **TQ Square Value:** Square each letter's TQ value, then sum.  
    
  - *Example:* LIGHT \= L(1²=1) \+ I(0²=0) \+ G(11²=121) \+ H(3²=9) \+ T(9²=81) \= 212


- **TQ Triangular Value:** Use the triangular number of each letter's TQ value.  
    
  - *Example:* LIGHT \= L(triangular of 1 \= 1\) \+ I(triangular of 0 \= 0\) \+ G(triangular of 11 \= 66\) \+ H(triangular of 3 \= 6\) \+ T(triangular of 9 \= 45\) \= 118  
  - *Note:* Triangular number of n \= n(n+1)/2


- **TQ Letter Position:** Multiply each letter's TQ value by its position in the word, then sum.  
    
  - *Example:* LIGHT \= L(1×1=1) \+ I(0×2=0) \+ G(11×3=33) \+ H(3×4=12) \+ T(9×5=45) \= 91  
  - *Note:* Position is counted from 1 (first letter) to n (last letter)

