package marytts.io.serializer;

import java.io.File;
import marytts.data.Utterance;
import marytts.io.MaryIOException;

/**
 *
 *
 * @author <a href="mailto:slemaguer@coli.uni-saarland.de">Sébastien Le
 *         Maguer</a>
 */
public interface Serializer {
    public Object export(Utterance utt) throws MaryIOException;

    public Utterance load(String content) throws MaryIOException;
}
