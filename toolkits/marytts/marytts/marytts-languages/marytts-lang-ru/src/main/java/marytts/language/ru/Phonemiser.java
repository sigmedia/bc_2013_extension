/**
 * Copyright 2002 DFKI GmbH.
 * All Rights Reserved.  Use is subject to license terms.
 *
 * This file is part of MARY TTS.
 *
 * MARY TTS is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, version 3 of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

package marytts.language.ru;

// Configuration
import marytts.config.MaryConfiguration;
import marytts.config.MaryConfigurationFactory;

// Exceptions
import marytts.exceptions.MaryConfigurationException;
import marytts.MaryException;

// Phonetic
import marytts.phonetic.AlphabetFactory;

// Locale
import java.util.Locale;

/**
 * The phonemiser module -- java implementation.
 *
 * @author Marc Schr&ouml;der
 */

public class Phonemiser extends marytts.modules.nlp.JPhonemiser {

    public Phonemiser() throws MaryConfigurationException {
        super(new Locale("ru"));
    }

    public void startup() throws MaryException {
        super.startup();

	// Apply the configuration
	MaryConfigurationFactory.getConfiguration("ru").applyConfiguration(this);

        // Set some resources
	setAllophoneSet(this.getClass().getResourceAsStream("/marytts/language/ru/lexicon/allophones.ru.xml"));
	setLexicon(this.getClass().getResourceAsStream("/marytts/language/ru/lexicon/ru_lexicon.fst"));
	setLetterToSound(this.getClass().getResourceAsStream("/marytts/language/ru/lexicon/ru.lts"));

        // Generate and add alphabet
        alphabet_convertor = AlphabetFactory.getAlphabet("russian_alphabet");
    }}
