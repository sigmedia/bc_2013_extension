/**
 * Copyright 2011 DFKI GmbH.
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

// Module part
import marytts.modules.MaryModule;
import marytts.modules.ModuleRegistry;
import marytts.modules.nlp.JPhonemiser;

// Configuration part
import marytts.config.MaryConfigurationFactory;
import marytts.config.MaryConfiguration;
import marytts.config.JSONMaryConfigLoader;

// Runtim
import marytts.runutils.Request;

// Locale
import java.util.Locale;

import org.testng.Assert;
import org.testng.annotations.*;

/**
 * Some more coverage tests with actual language modules
 *
 * @author marc
 *
 */
public class MaryIT extends marytts.MaryIT {



    /*****************************************************************************
     ** USJPhonemiser test
     *****************************************************************************/
    @Test
    public void testIsPosPunctuation() throws Exception {
        JPhonemiser phonemiser = (JPhonemiser) ModuleRegistry.getDefaultModule(Phonemiser.class.getName());
	Assert.assertNotNull(phonemiser);
	MaryConfigurationFactory.getConfiguration("ru").applyConfiguration(phonemiser);

        Assert.assertTrue(phonemiser.isPosPunctuation("."));
        Assert.assertTrue(phonemiser.isPosPunctuation(","));
        Assert.assertTrue(phonemiser.isPosPunctuation(":"));
        Assert.assertFalse(phonemiser.isPosPunctuation("NN"));
    }

    @Test
    public void testMaybePronounceable() throws Exception {
        JPhonemiser phonemiser = (JPhonemiser) ModuleRegistry.getDefaultModule(Phonemiser.class.getName());
        Assert.assertNotNull(phonemiser);
        MaryConfigurationFactory.getConfiguration("ru").applyConfiguration(phonemiser);

        Assert.assertFalse(phonemiser.maybePronounceable(null, "NN"));
        Assert.assertFalse(phonemiser.maybePronounceable(null, "."));
        Assert.assertFalse(phonemiser.maybePronounceable("", "NN"));
        Assert.assertFalse(phonemiser.maybePronounceable("", "."));
        Assert.assertTrue(phonemiser.maybePronounceable("foo", "NN"));
        Assert.assertTrue(phonemiser.maybePronounceable("foo", "."));
        Assert.assertTrue(phonemiser.maybePronounceable("@", "NN"));
        Assert.assertFalse(phonemiser.maybePronounceable("@", "."));
    }



    @Test
    public void testLTS() throws Exception {
        JPhonemiser phonemiser = (JPhonemiser) ModuleRegistry.getDefaultModule(Phonemiser.class.getName());
        Assert.assertNotNull(phonemiser);
        MaryConfigurationFactory.getConfiguration("ru").applyConfiguration(phonemiser);

        StringBuilder sb = new StringBuilder();
        Object t = phonemiser.phonemise("Привет", "NN", sb);
        Assert.assertNotNull(t);
    }

    // @Test
    // public void testUtterance() throws Exception {
    //     String input = "С югославской стороны в битве участвовали 4 дивизии общей численностью около 22 тысяч человек, в том числе около 4 тысяч больных и раненых.";

    //     // Read configuration
    //     MaryConfiguration conf = (new JSONMaryConfigLoader()).loadConfiguration(MaryIT.class.getResourceAsStream("test_conf.json"));

    //     Request req = new Request(conf, input);
    //     req.process();
    //     System.out.println(req.serializeFinaleUtterance());
    //     // Assert.assertFalse(true);
    // }
}
