package marytts.phonetic.converter;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;


/**
 *
 *
 * @author <a href="mailto:slemaguer@coli.uni-saarland.de">Sébastien Le Maguer</a>
 */
public class Arpabet extends Alphabet
{
    public Arpabet() {
	super();

        // Vowels
        this.addIpaCorrespondance("aa", "ɑ");
        this.addIpaCorrespondance("ae", "æ");
        this.addIpaCorrespondance("ah", "ʌ");
        this.addIpaCorrespondance("ao", "ɔ");
        this.addIpaCorrespondance("aw", "aʊ");
        this.addIpaCorrespondance("ax", "ə");
        this.addIpaCorrespondance("axr", "ɚ");
        this.addIpaCorrespondance("ay", "aɪ");
        this.addIpaCorrespondance("eh", "ɛ");
        this.addIpaCorrespondance("er", "ɝ");
        this.addIpaCorrespondance("ey", "eɪ");
        this.addIpaCorrespondance("ih", "ɪ");
        this.addIpaCorrespondance("ix", "ɨ");
        this.addIpaCorrespondance("iy", "i");
        this.addIpaCorrespondance("ow", "oʊ");
        this.addIpaCorrespondance("ow", "əʊ");
        this.addIpaCorrespondance("oy", "ɔɪ");
        this.addIpaCorrespondance("uh", "ʊ");
        this.addIpaCorrespondance("uw", "u");
        this.addIpaCorrespondance("ux", "ʉ");

        // Consonnants
        this.addIpaCorrespondance("b", "b");
        this.addIpaCorrespondance("ch", "tʃ");
        this.addIpaCorrespondance("d", "d");
        this.addIpaCorrespondance("dh", "ð");
        this.addIpaCorrespondance("dx", "ɾ");
        this.addIpaCorrespondance("el", "l̩");
        this.addIpaCorrespondance("em", "m̩");
        this.addIpaCorrespondance("en", "n̩");
        this.addIpaCorrespondance("f", "f");
        this.addIpaCorrespondance("g", "ɡ");
        this.addIpaCorrespondance("hh", "h");
        this.addIpaCorrespondance("jh", "dʒ");
        this.addIpaCorrespondance("k", "k");
        this.addIpaCorrespondance("l", "l");
        this.addIpaCorrespondance("m", "m");
        this.addIpaCorrespondance("n", "n");
        this.addIpaCorrespondance("ng", "ŋ");
        this.addIpaCorrespondance("nx", "ɾ̃");
        this.addIpaCorrespondance("p", "p");
        this.addIpaCorrespondance("q", "ʔ");
        this.addIpaCorrespondance("r", "ɹ");
        this.addIpaCorrespondance("r", "r");
        this.addIpaCorrespondance("s", "s");
        this.addIpaCorrespondance("sh", "ʃ");
        this.addIpaCorrespondance("t", "t");
        this.addIpaCorrespondance("th", "θ");
        this.addIpaCorrespondance("v", "v");
        this.addIpaCorrespondance("w", "w");
        this.addIpaCorrespondance("wh", "ʍ");
        this.addIpaCorrespondance("y", "j");
        this.addIpaCorrespondance("z", "z");
        this.addIpaCorrespondance("zh", "ʒ");
    }
}
