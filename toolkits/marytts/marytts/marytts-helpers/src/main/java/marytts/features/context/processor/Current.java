package marytts.features.context.processor;

import marytts.MaryException;

import marytts.data.Utterance;
import marytts.data.item.Item;

import marytts.features.context.ContextProcessor;

/**
 * Context processor to get the current item. This class is here to be
 * consistent with the whole feature processing architecture.
 *
 * @author <a href="mailto:slemaguer@coli.uni-saarland.de">Sébastien Le
 *         Maguer</a>
 */
public class Current implements ContextProcessor {

    /**
     * Return the given item
     *
     * @param utt the utterance
     * @param item
     *            the returned item
     * @return the item given in parameter
     * @throws Exception
     *             not throwed actually
     */
    public Item get(Utterance utt, Item item) throws MaryException {
        return item;
    }
}
