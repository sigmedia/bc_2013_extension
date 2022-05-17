package marytts

// Gradle
import org.gradle.api.*
import org.gradle.api.tasks.Copy
import org.gradle.internal.os.OperatingSystem

// Task specificx
import marytts.tasks.GenerateDict

class MaryTTSGenerateDictionaryPlugin implements Plugin<Project> {

    @Override
    void apply(Project project) {

        project.configurations {
            marytts
        }

        project.repositories {
            mavenLocal()
            jcenter()
            ivy {
                url 'https://github.com/marytts/montreal-forced-aligner-release-assets/archive'
                layout 'pattern', {
                    artifact '[revision]-[classifier].[ext]'
                }
            }
            maven {
                url 'https://oss.jfrog.org/artifactory/oss-release-local'
            }
        }

        project.dependencies {
            marytts 'de.dfki.mary:marytts-lang-en:6.0.1-SNAPHOT'
        }

        project.task('generateDictionary', type: GenerateDict) {
            group = 'MFA'
            description = 'Extract the dictionary and save the utterances in the JSON format'
            // locale = Locale.US // FIXME needs to see about this
            srcDir = project.layout.buildDirectory.dir('text')
            destDir = project.layout.buildDirectory.dir('utt_json')
            dictFile = project.layout.buildDirectory.file('dict.txt')
        }
    }
}
