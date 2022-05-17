package marytts.features.feature.processor.phone;

import java.util.ArrayList;
import marytts.MaryException;

import marytts.data.Utterance;
import marytts.data.item.Item;
import marytts.data.Sequence;
import marytts.data.Relation;
import marytts.data.SupportedSequenceType;


import marytts.data.item.linguistic.Word;
import marytts.data.item.phonology.NSS;
import marytts.data.item.phonology.Phoneme;

import marytts.features.Feature;
import marytts.features.feature.FeatureProcessor;

import java.util.Hashtable;

/**
 *
 *
 * @author <a href="mailto:slemaguer@coli.uni-saarland.de">Sébastien Le
 *         Maguer</a>
 */
public class NSSPunctuation implements FeatureProcessor {

    public NSSPunctuation() {
    }

    public Feature generate(Utterance utt, Item item) throws MaryException {
        if (item instanceof marytts.data.item.phonology.NSS) {

            Sequence<Item> seq_item = (Sequence<Item>) item.getSequence();
            Relation rel = utt.getRelation(seq_item, utt.getSequence(SupportedSequenceType.WORD));
            int item_idx = seq_item.indexOf(item);

            ArrayList<Word> words = (ArrayList<Word>) rel.getRelatedItems(item_idx);
            if (words.size() == 0)
                return Feature.UNDEF_FEATURE;

            if (words.size() == 1) {
                return new Feature(words.get(0).getText());
            }

            return Feature.UNDEF_FEATURE;
        } else if (item instanceof marytts.data.item.phonology.Phoneme) {
            return Feature.UNDEF_FEATURE;
        }

        throw new MaryException("Only a phone or a nss is accepted not an item of type " + item.getClass().toString() +
                            " ("
                            + item.toString() + ")");
    }
}
