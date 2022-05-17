package marytts

// Gradle
import org.gradle.api.*
import org.gradle.api.tasks.Copy
import org.gradle.internal.os.OperatingSystem

// Task specificx
import marytts.tasks.*

class MaryTTSGenerateLinguisticFeaturesPlugin implements Plugin<Project> {

    @Override
    void apply(Project project) {

        project.configurations {
            marytts
            jtgt
        }

        project.repositories {
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
            marytts 'de.dfki.mary:marytts-common:6.0.1-SNAPHOT'
            jtgt 'org.m2ci.msp:jtgt:0.6.1'
        }

        project.task('addDurationToUtt', type: AddDurationToUtt) {
            description = 'Add duration to segment sequence'
            phTierName = "phones"
            // locale = Locale.US // FIXME needs to see about this

            srcUttDir = project.layout.buildDirectory.dir('utt_json')
            srcTextGridDir = project.layout.buildDirectory.dir('TextGrid')
            destUttDir = project.layout.buildDirectory.dir('utt_json_with_dur')
        }

        project.task('generateHTSLabels', type: GenerateHTSLabels) {
            description = 'Generate HTS label files'
            // locale = Locale.US // FIXME needs to see about this
            srcDir = project.addDurationToUtt.destUttDir
            fullLabDir = project.layout.buildDirectory.dir('hts_labels/full')
            monoLabDir = project.layout.buildDirectory.dir('hts_labels/mono')
        }
    }
}
