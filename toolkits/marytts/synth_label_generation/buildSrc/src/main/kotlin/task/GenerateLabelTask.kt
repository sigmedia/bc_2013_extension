package task

// Logging
import org.apache.log4j.Logger

// Java IO
import java.io.File
import java.io.Serializable

// Injection
import javax.inject.Inject

// Gradle baseline
import org.gradle.api.*
import org.gradle.api.model.*

// Worker/Task
import org.gradle.api.tasks.*
import org.gradle.workers.*

// Provider/lazy configuration
import org.gradle.api.file.*
import org.gradle.api.provider.*

// MaryTTS
import marytts.runutils.*;
import marytts.config.JSONMaryConfigLoader;
import marytts.config.MaryConfiguration;

/**
*  Task which uses MaryTTS to generate HTS Label files given a list of texts
*
*  @property objects The object factory to deal with lazy configuration
*  @property workerExecutor The worker executor used by gradle
*  @constructor Creates the task
*/
open class GenerateLabelTask @Inject constructor(objects: ObjectFactory, @Internal val workerExecutor: WorkerExecutor): DefaultTask()
{
    @InputFile
    val list_file: RegularFileProperty = objects.fileProperty()

    @InputDirectory
    val text_dir: DirectoryProperty = objects.directoryProperty()

    @OutputDirectory
    val full_label_dir: DirectoryProperty = objects.directoryProperty()

    @OutputDirectory
    val mono_label_dir: DirectoryProperty = objects.directoryProperty()

    @Input
    val configuration: Property<MaryConfiguration> = objects.property(MaryConfiguration::class.java)

    /**
    *  Task core function
    */
    @TaskAction
    fun run() {
        list_file.get().asFile.forEachLine { basename ->
            val text_file: File = File(text_dir.get().asFile, basename.trim() + ".txt")
            val full_label_file: File = File(full_label_dir.get().asFile, basename.trim() + ".lab")
            val mono_label_file: File = File(mono_label_dir.get().asFile, basename.trim() + ".lab")

            // Define parameters
            val params: GenerateLabelWorkerParameters =
                GenerateLabelWorkerParameters(text_file, full_label_file,
                                              mono_label_file, configuration.get())
            val conf: GenerateLabelWorkerConfiguration = GenerateLabelWorkerConfiguration(params)

            // Submit the execution
            workerExecutor.submit(GenerateLabelWorker::class.java, conf)
        }
    }
}


/**
* Configures the worker with IsolationMode.NONE and the GenerateLabelWorkerParameters.
*
*/
class GenerateLabelWorkerConfiguration(val parameters: GenerateLabelWorkerParameters): Action<WorkerConfiguration> {
    override fun execute(workerConfiguration: WorkerConfiguration) {
        workerConfiguration.isolationMode = IsolationMode.NONE
        workerConfiguration.setParams(parameters)
    }
}


/**
* Serializable stateless parameters that are needed by the GenerateLabelWorker.
*
*/
data class GenerateLabelWorkerParameters(
    val text_file: File,
    val full_label_file: File,
    val mono_label_file: File,
    val configuration: MaryConfiguration
) : Serializable

/**
*  Worker which MaryTTS to generate HTS Label files given a list of texts
*
*  @Constructor Creates the worker
*/
class GenerateLabelWorker @Inject constructor(params: GenerateLabelWorkerParameters): Runnable {
    private val logger: Logger = Logger.getLogger(GenerateLabelWorker::class.java.name)

    val parameters: GenerateLabelWorkerParameters = params

    val vowels: Set<String> = hashSetOf("aa", "ae", "ah", "ao", "aw", "ax", "axr", "ay", "eh", "er", "ey", "ih", "ix", "iy", "ow", "ow", "oy", "uh", "uw", "ux")

    val accent_regex = "^.*/B:([a-z0-9]*)-([a-z0-9]*)-".toRegex()
    val mono_regex = "^[^-]*-([^+]*)[+]".toRegex()

    fun addStress(mono_label: String, full_label: String): String {
        if (vowels.contains(mono_label)) {
            val m = accent_regex.find(full_label)
            val (accent, stress) = m!!.destructured
            return "${accent}${stress}"
        } else {
            return "";
        }
    }

    /**
     *  Running function
     *
     */
    override fun run() {
            // Prepare request
            val text = parameters.text_file.readText(Charsets.UTF_8)
            val request: Request = Request(parameters.configuration, text)

            // Process request
            request.process()

            // Get the labels
            val full_label: String = request.serializeFinaleUtterance().toString()
            parameters.full_label_file.writeText(full_label)

            // Convert full to mono
            var mono_label_list: MutableList<String> = mutableListOf<String>()
            full_label.lines().forEach { full_lab ->
                if (full_lab != "") {
                    val m = mono_regex.find(full_lab)
                    val (mono_lab) = m!!.destructured
                    val stress: String = addStress(mono_lab, full_lab)
                    mono_label_list.add("${mono_lab}${stress}")
                }
            }

            parameters.mono_label_file.writeText(mono_label_list.joinToString("\n"))

    }
}
