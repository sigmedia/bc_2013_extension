/**
 * Copyright 2000-2006 DFKI GmbH.
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
package marytts;

// IO
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;

// Mary IO
import marytts.io.MaryIOException;
import marytts.io.serializer.ROOTSJSONSerializer;
import marytts.io.serializer.XMLSerializer;

// Mary general
import marytts.config.MaryConfigurationFactory;
import marytts.data.Utterance;
import marytts.modules.MaryModule;
import marytts.runutils.Mary;
import marytts.runutils.MaryState;
import marytts.util.MaryUtils;

// Log
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.core.config.LoggerConfig;
import org.apache.logging.log4j.core.config.Configuration;
import org.apache.logging.log4j.core.LoggerContext;

// Test
import org.testng.Assert;
import org.testng.ITestContext;
import org.testng.annotations.*;

// Helper
import java.lang.reflect.Method;

/**
 * @author Sébastien Le Maguer
 *
 *
 */
public class MaryIT {

    protected Logger logger;

    @BeforeClass(alwaysRun = true)
    protected void setUp() throws Exception
    {
        logger = LogManager.getLogger(this.getClass());
	LoggerContext ctx = (LoggerContext) LogManager.getContext(false);
	Configuration config = ctx.getConfiguration();
	LoggerConfig loggerConfig = config.getLoggerConfig(LogManager.ROOT_LOGGER_NAME);
	loggerConfig.setLevel(Level.DEBUG);
	ctx.updateLoggers();

        synchronized(Mary.class) {
            Mary.startup();

            if (Mary.getCurrentState() != MaryState.RUNNING)
                throw new Exception("Mary is not started!");

            Assert.assertNotNull(MaryConfigurationFactory.getDefaultConfiguration());
        }
    }


    @AfterClass(alwaysRun = true)
    public void shutdown() throws Exception {
        Mary.shutdown();
    }

    @BeforeMethod
    public void startTest(final Method method) {
        logger.debug("###################################################################################################");
        logger.debug("## Starting test " + method.getName());
        logger.debug("###################################################################################################\n");
    }

    @AfterMethod
    public void endTest(final Method method) {
        logger.debug("###################################################################################################");
        logger.debug("## Ending test " + method.getName());
        logger.debug("###################################################################################################\n\n");
    }

    protected Utterance loadXMLResource(String resourceName) throws IOException, MaryIOException {
        // Define a reader to the resource
        BufferedReader br = new BufferedReader(
                                               new InputStreamReader(this.getClass().getResourceAsStream(resourceName), "UTF-8"));

        // Loading the XML content file into a string
        StringBuilder buf = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            buf.append(line);
            buf.append("\n");
        }
        String document = buf.toString();

        // Using serializer to extract the utterance the from "string" document
        XMLSerializer xml_ser = new XMLSerializer();
        Utterance utt = xml_ser.load(document);

        // Return loaded utterance
        return utt;
    }

    protected boolean processAndCompare(String in, String target_out, String configuration_id, MaryModule module) throws Exception {
	MaryConfigurationFactory.getConfiguration(configuration_id).applyConfiguration(module);
        Utterance input = loadXMLResource(in);
        Utterance targetOut = loadXMLResource(target_out);
        Utterance processedOut = module.process(input);

        ROOTSJSONSerializer out_ser = new ROOTSJSONSerializer();
        logger.debug(" ======================== expected =====================");
        logger.debug(out_ser.export(targetOut));
        logger.debug(" ======================== achieved =====================");
        logger.debug(out_ser.export(processedOut));
        logger.debug(" =======================================================");

        return targetOut.equals(processedOut);
    }

}
