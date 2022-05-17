package marytts.language.ru.phonetic;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;

import marytts.phonetic.converter.Alphabet;


/**
 *
 *
 * @author <a href="mailto:slemaguer@coli.uni-saarland.de">Sébastien Le Maguer</a>
 */
public class RussianAlphabet extends Alphabet
{
    public RussianAlphabet() {
	super();

        // Consonnants
        this.addIpaCorrespondance("b", "b");
        this.addIpaCorrespondance("bb", "bʲ");
        this.addIpaCorrespondance("c", "ts");
        // this.addIpaCorrespondance("ch", "tɕ");    // FIXME: double check
        this.addIpaCorrespondance("ch", "tʃ");
        this.addIpaCorrespondance("d", "d");
        this.addIpaCorrespondance("dd", "dʲ");
        this.addIpaCorrespondance("f", "f");
        this.addIpaCorrespondance("ff", "fʲ");
        this.addIpaCorrespondance("g", "ɡ");
        this.addIpaCorrespondance("gg", "ɡʲ");
        this.addIpaCorrespondance("h", "h");
        this.addIpaCorrespondance("hh", "hʲ");
        this.addIpaCorrespondance("j", "j");
        this.addIpaCorrespondance("k", "k");
        this.addIpaCorrespondance("kk", "kʲ");
        this.addIpaCorrespondance("l", "l");
        this.addIpaCorrespondance("ll", "lʲ");
        this.addIpaCorrespondance("m", "m");
        this.addIpaCorrespondance("mm", "mʲ");
        this.addIpaCorrespondance("n", "n");
        this.addIpaCorrespondance("nn", "nʲ");
        this.addIpaCorrespondance("p", "p");
        this.addIpaCorrespondance("pp", "pʲ");
        this.addIpaCorrespondance("r", "r");
        this.addIpaCorrespondance("rr", "rʲ");
        this.addIpaCorrespondance("s", "s");
        this.addIpaCorrespondance("sch", "ɕ");   // FIXME: double check
        // this.addIpaCorrespondance("sh", "ʂ");    // FIXME: double check
        this.addIpaCorrespondance("sh", "ʃ");    // FIXME: double check
        this.addIpaCorrespondance("ss", "sʲ");
        this.addIpaCorrespondance("t", "t");
        this.addIpaCorrespondance("tt", "tʲ");
        this.addIpaCorrespondance("v", "v");
        this.addIpaCorrespondance("vv", "vʲ");
        this.addIpaCorrespondance("z", "z");
        this.addIpaCorrespondance("zh", "ʒ");    // FIXME: double check
        this.addIpaCorrespondance("zz", "zʲ");



        // Stressed vowels
        this.addIpaCorrespondance("ii", "iˈ");
        this.addIpaCorrespondance("yy", "yˈ");
        this.addIpaCorrespondance("uu", "uˈ");
        this.addIpaCorrespondance("ee", "eˈ");
        this.addIpaCorrespondance("oo", "oˈ");
        this.addIpaCorrespondance("aa", "aˈ");

        // First level of reduction
        this.addIpaCorrespondance("a", "a");
        this.addIpaCorrespondance("e", "e");
        this.addIpaCorrespondance("i", "i");
        this.addIpaCorrespondance("y", "y");
        this.addIpaCorrespondance("u", "u");

        // Second level of reduction
        this.addIpaCorrespondance("ae", "ɛ"); // FIXME: double check
        this.addIpaCorrespondance("ay", "ə"); // FIXME: double check
        this.addIpaCorrespondance("ur", "ʉ"); // FIXME: double check

    }
}
