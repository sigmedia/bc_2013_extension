package marytts.io.serializer

import marytts.data.SupportedSequenceType
import marytts.data.Utterance;
import marytts.data.Sequence;
import marytts.data.item.linguistic.Word;
import marytts.io.MaryIOException;
import marytts.io.serializer.Serializer;

/**
 *
 *
 */
public class MFASerializer implements Serializer {

    /**
     * Constructor
     *
     */
    public UtteranceSerializer() {
    }

    public Object export(Utterance utt) throws MaryIOException {
        try {

            // Get mary information
            def words = utt.getSequence(SupportedSequenceType.WORD);
            def rel_ph = utt.getRelation(SupportedSequenceType.WORD, SupportedSequenceType.PHONE)
            def rel_nss = utt.getRelation(SupportedSequenceType.WORD, SupportedSequenceType.NSS)
            
            def ph = [:]
            for (int i=0; i<words.size(); i++) {
                if (rel_ph.getRelatedItems(i).size() > 0) {
                    ph[words[i].toString()] = rel_ph.getRelatedItems(i).join(" ")
                }
            }

            return ph;
        } catch (Exception ex) {
            throw new MaryIOException("Cannot serialize utt", ex);
        }
    }

    /**
     * Unsupported operation ! We can't import from a TSV formatted input.
     *
     * @param content
     *            unused
     * @return nothing
     * @throws MaryIOException
     *             never done
     */
    public Utterance load(String content) throws MaryIOException {
        throw new UnsupportedOperationException();
    }
}
