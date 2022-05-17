package marytts.tasks

import org.gradle.api.DefaultTask
import org.gradle.api.file.DirectoryProperty
import org.gradle.api.file.RegularFileProperty
import org.gradle.api.tasks.*
import org.gradle.api.provider.Property

// Configuration
import marytts.config.MaryConfiguration
import marytts.config.JSONMaryConfigLoader

// Runtime / Request
import marytts.runutils.Request

// IO
import marytts.io.serializer.Serializer
import marytts.io.serializer.MFASerializer
import marytts.io.serializer.ROOTSJSONSerializer
import marytts.data.Utterance


class GenerateDict extends DefaultTask {

    @Input
    final Property<String> locale = project.objects.property(String)

    @InputDirectory
    final DirectoryProperty srcDir = project.objects.directoryProperty()

    @OutputDirectory
    final DirectoryProperty destDir = project.objects.directoryProperty()

    @OutputFile
    final RegularFileProperty dictFile = project.objects.fileProperty()

    @TaskAction
    void convert() {
        // Read the configuration
        MaryConfiguration conf_object = null
        try {
            InputStream configuration_stream = this.class.getResourceAsStream("/marytts/${locale.get()}.json")
            conf_object = (new JSONMaryConfigLoader()).loadConfiguration(configuration_stream);
        } catch (Exception ex) {
            project.logger.error "${locale.get()} configuration couldn't be done : ${ex}"
            throw ex
        }


        // Call Mary
        def dict = [:]
        project.fileTree(srcDir).include('*.txt').collect { txtFile ->
            try {
                // Read the text
                String input_data = txtFile.text;

                // Call mary && Get the output utterance
                def request = new Request(conf_object, input_data);
                request.process();
                Utterance utt = (Utterance) request.serializeFinaleUtterance();

                // Apply dedicated serializer and fill the dict
                Serializer utt_serializer = new MFASerializer();
                def output = utt_serializer.export(utt)
                output.each { k,v ->
                    dict[k] = v
                }

                // Apply dedicated serializer and save the UTT
                utt_serializer = new ROOTSJSONSerializer()
                output = utt_serializer.export(utt);
                destDir.file(txtFile.name - '.txt' + '.json').get().asFile.withWriter('UTF-8') { out ->
                    out.println output
                }

            } catch (Exception ex) {
                project.logger.error "Excluding $txtFile.name : ${ex}"
                // FIXME: more detail message
            }
        }

        // Save dictionnary
        dictFile.get().asFile.withWriter('UTF-8') { out ->
            dict.toSorted { it.key.toString()toLowerCase() }.each { word, phonemes ->
                out.println "$word $phonemes"
            }
        }
    }
}
