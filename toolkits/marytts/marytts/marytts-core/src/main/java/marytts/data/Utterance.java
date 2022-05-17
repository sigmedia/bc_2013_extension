package marytts.data;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Hashtable;
import java.util.Set;

import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import marytts.MaryException;
import marytts.data.item.Item;

/**
 * The Utterance is the entry point to the data used in MaryTTS. It is a
 * container to access to all the information computed during the process.
 *
 * @author <a href="mailto:slemaguer@coli.uni-saarland.de">Sébastien Le Maguer</a>
 */
public class Utterance {
    /** FIXME: temp feature names, nowhere else to put for now */
    private ArrayList<String> m_feature_names;

    /**
     * The sequences which contains the data of the utterance. Organized by type
     * for now
     */
    private Hashtable<String, Sequence<? extends Item>> m_sequences;

    /** The relation graph to link te sequences */
    private RelationGraph m_relation_graph;

    /** The set of "not computed" relation based on types */
    private Set<ImmutablePair<String, String>> m_available_relation_set;

    /** The logger of the utterance */
    protected static Logger logger = LogManager.getLogger(Utterance.class);

    /**
     * The constructor of the utterance which forces to define a text and an
     * associated locale
     *
     * @param text
     *            the original text of the utterance
     * @param locale
     *            the locale used for this utterance
     */
    public Utterance() {
        m_sequences = new Hashtable<String, Sequence<? extends Item>>();
        m_available_relation_set = new
        HashSet<ImmutablePair<String, String>>();
        m_relation_graph = new RelationGraph();
	m_feature_names = new ArrayList<String>();
    }

    /***************************************************************************************************************
     ** Sequence methods
     ***************************************************************************************************************/

    /**
     * Adding a sequence of a specified type. If the type is already existing,
     * the corresponding sequence is replaced.
     *
     * @param type
     *            the type of the sequence
     * @param sequence
     *            the sequence
     */
    public void addSequence(String type, Sequence<? extends Item> sequence) {
        m_sequences.put(type, sequence);
    }

    /**
     * Method to check if a sequence of a certain type is already defined.
     *
     * @param type
     *            the type to check
     * @return true if a sequence of the given type is already defined, false
     *         else
     */
    public boolean hasSequence(String type) {
        return m_sequences.containsKey(type);
    }

    /**
     * Method to get the sequence knowing the type
     *
     * @param type
     *            the type of the sequence
     * @return the found sequence or an empty sequence
     */
    public Sequence<? extends Item> getSequence(String type) {
        if (m_sequences.containsKey(type)) {
            return m_sequences.get(type);
        }

        return new Sequence<Item>();
    }

    /**
     * Remove the sequence of the given type
     *
     * @param type the type of the sequence to remove
     */
    public void removeSequence(String type) {
        if (! hasSequence(type))
            return;

        Sequence<? extends Item> cur_seq = getSequence(type);

        // delete relation
        Set<ImmutablePair<String, String>> set_rel_to_be_remove = new HashSet<ImmutablePair<String, String>>();
        for (ImmutablePair<String, String> cur_rel: m_available_relation_set) {
            if (cur_rel.getLeft().equals(type)) {
                set_rel_to_be_remove.add(cur_rel);
            } else if (cur_rel.getRight().equals(type)) {
                set_rel_to_be_remove.add(cur_rel);
            }
        }

        for (ImmutablePair<String, String> cur_rel: set_rel_to_be_remove) {
            removeRelation(cur_rel.getLeft(), cur_rel.getRight());
        }
        m_relation_graph.removeSequence(cur_seq);

        // Delete sequence
        cur_seq.clear();
        m_sequences.remove(type);
    }

    /**
     * Get all the available sequence types
     *
     * @return the available sequence types
     */
    public Set<String> listAvailableSequences() {
        return m_sequences.keySet();
    }

    /**************************************************************************************************************
     ** Relation methods
     **************************************************************************************************************/
    /**
     * Get the relation based on the source type and the target type
     *
     * @param source
     *            the type of the source sequence
     * @param target
     *            the type of the target sequence
     * @return the found relation between the source sequence of type source and
     *         the target sequence of type target
     * @throws MaryException if there is no exception
     */
    public Relation getRelation(String source, String target) throws MaryException {
        return getRelation(getSequence(source), getSequence(target));
    }

    /**
     * Get the relation between a given source and a given target sequence
     *
     * @param source the source sequence
     * @param target the target sequence
     * @return the relation
     * @throws MaryException if the relation doesn't exist
     */
    public Relation getRelation(Sequence<? extends Item> source, Sequence<? extends Item> target) throws MaryException {

        Relation rel =  m_relation_graph.getRelation(source, target);

        if (rel == null) {
            throw new MaryException(String.format("Cannot find relation between \"%s\" and \"%s\"", source, target));
        }

        return rel;
    }

    /**
     * Remove the relation between a given source and a given target sequence
     *
     * @param source the source sequence
     * @param target the target sequence
     */
    public void removeRelation(String source, String target) {
        m_relation_graph.removeRelation(getSequence(source), getSequence(target));
        m_available_relation_set.remove(new ImmutablePair<String, String>(source, target));
    }

    /**
     * Get the relation based on the source type and the target type
     *
     * @param source
     *            the type of the source sequence
     * @param target
     *            the type of the target sequence
     */
    public void setRelation(String source, String target, Relation rel) {
        m_relation_graph.addRelation(rel);
        m_available_relation_set.add(new ImmutablePair<String, String>(source, target));
    }

    /**
     * List all the relations which are not computed through the graph. The
     * results is a Set of couple (source sequence type, target sequence type).
     *
     * @return the set of all relations.
     */
    public Set<ImmutablePair<String, String>> listAvailableRelations() {
        return m_available_relation_set;
    }

    /**********************************************************************************************************
     ** Object overriding
     **********************************************************************************************************/
    /**
     * Method to determine if an object is equal to the current utterance.
     *
     * @param obj
     *            the object to compare
     * @return true if the object is an utterance and equals the current one,
     *         false else
     */
    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof Utterance)) {
            return false;
        }

        Utterance utt = (Utterance) obj;

        if (!utt.m_sequences.keySet().equals(m_sequences.keySet())) {
            logger.debug("Sequences availables are not the same in both utterances: {" + m_sequences.keySet() +
                         "} vs {"
                         + utt.m_sequences.keySet() + "}");
            return false;
        }

        boolean not_equal = false;
        for (String type : m_sequences.keySet()) {

            Sequence<Item> cur_seq = (Sequence<Item>) m_sequences.get(type);
            Sequence<Item> other_seq = (Sequence<Item>) m_sequences.get(type);

            if (cur_seq.size() != other_seq.size()) {
                logger.debug(" => " + type + " is not leading to equal sequences (size difference)");
                break;
            }

            for (int i = 0; i < cur_seq.size(); i++) {
                Item cur_item = cur_seq.get(i);
                Item other_item = other_seq.get(i);
                if (!other_item.equals(cur_item)) {
                    not_equal = true;

                    logger.debug(" => " + type + " is not leading to equal sequences");
                    break;
                }
            }

            if (not_equal) {
                break;
            }
        }

        if (not_equal) {
            return false;
        }

        if (!m_available_relation_set.equals(utt.m_available_relation_set)) {
            return false;
        }

        return true;
    }



    /***************************************************************************************************************
     ** Helpers
     ***************************************************************************************************************/
    /**
     *
     */
    public void mergeInto(Utterance alternate, Relation linking_rel) throws MaryException{
        String src_label="", tgt_label="";
        for (String seq_label: listAvailableSequences()) {
            if (linking_rel.getSource() == this.getSequence(seq_label)) {
                src_label = seq_label;
                break;
            }
        }

        // Add needed sequence
        for (String seq_label: alternate.listAvailableSequences()) {
            // We don't care about the same sequences!
            if (hasSequence(seq_label)) {
                logger.debug(seq_label + " already available in current utterance");
            } else {
                logger.debug("adding " + seq_label + " to the current utterance");
                this.addSequence(seq_label, alternate.getSequence(seq_label));
            }

            if (alternate.getSequence(seq_label) == linking_rel.getTarget())
                tgt_label = seq_label;
        }

        // Add the relations
        for (ImmutablePair<String, String> id_pair: alternate.listAvailableRelations()) {
            Relation rel = alternate.getRelation(id_pair.getLeft(), id_pair.getRight());
            this.setRelation(id_pair.getLeft(), id_pair.getRight(), rel);
        }

        // Finalize the linking
        if (src_label.equals(""))
            throw new MaryException("Source sequence for the linking is not found, linking relation is invalid");

        if (tgt_label.equals(""))
            throw new MaryException("Target sequence for the linking is not found, linking relation is invalid");

        this.setRelation(src_label, tgt_label, linking_rel);
    }


    /***************************************************************************************************************
     ** Temporary
     ***************************************************************************************************************/
    public ArrayList<String> getFeatureNames() {
	return m_feature_names;
    }

    public void setFeatureNames(ArrayList<String> feature_names) {
	m_feature_names = feature_names;
    }
}
