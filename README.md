# ume-saami-conv
Orthography conversion for Ume Saami

## Description

This is a conversion script implementing a mechanical conversion from Wolfgang Schlachter's (1958)
dictionary spelling to current Ume Saami orthography (approved 2016, dictionary by
Henrik Barruk 2018).

The conversion has a number of known shortcomings partly due to the peculiarities of
Schlachter's markup and source dialect.
For instance some non-initial-syllable vowel conversions can not be automatized correctly due to syncope phenomena.
The distinction between back /ï/ and front /i/ is not consistently deducible from Schlachter's 
spelling, so only /i/ is used here as well. 
Also the phoneme /đ/ (~ /r/) is represented by d in Schlachter and thus undifferentiable from 
a normal /d/.

The converted spelling is more detailed than the standard in that overlong geminates are
marked with a straight apostrophe /'/, e.g. /beäg'ga/ ’storm’ (can be optionally turned off).
The distinction between long (open) /å/ and short (closed) /o/, which is not
marked in the standard orthography, can also optionally be retained; see Usage.
The superscript vertical line, which Schlachter occasionally uses to mark an elided 
(or overshort) vowel between 2nd and 3rd syllable, is converted to a curly apostrophe /’/.

## Usage

By default, the program converts all input text and outputs the result.
The -f option can be used to only convert a single (TAB-separated) column of each input line.

Optional arguments:
```
  -h, --help           show help message and exit
  -f [N], --field [N]  Convert only given field (column) and insert the result
                       to the beginning of line. -f without N uses the first
                       field.
  -G, --no_overlong    Disable overlong geminate marking with /'/
  -o, --short_o        Distinguish short /o/ from long /å/ (default: output
                       both as /å/)
```

## License

See [LICENSE](LICENSE).
