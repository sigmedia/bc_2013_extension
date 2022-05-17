package de.dfki.mary.voicebuilding

import org.gradle.testkit.runner.GradleRunner
import org.testng.annotations.BeforeSuite
import org.testng.annotations.DataProvider
import org.testng.annotations.Test

import static org.gradle.testkit.runner.TaskOutcome.SUCCESS
import static org.gradle.testkit.runner.TaskOutcome.UP_TO_DATE

class MaryttsKaldiMfaPluginFunctionalTest {

    GradleRunner gradle

    @BeforeSuite
    void setup() {
        def projectDir = File.createTempDir()
        gradle = GradleRunner.create().withProjectDir(projectDir).withPluginClasspath().forwardOutput()
        new File(projectDir, 'build.gradle').withWriter {
            it << this.class.getResourceAsStream('build.gradle')
        }
    }

    @DataProvider
    Object[][] taskNames() {
        // task name to run, and whether to chase it with a test task named "testName"
        [
                ['help', false],
                ['testPlugin', false],
                ['unpackMFA', true],
                ['generateMFALabAndDictionary', true],
                ['prepareForcedAlignment', true],
                ['runForcedAlignment', true],
                ['convertTextGridToXLab', true]
        ]
    }

    @Test(dataProvider = 'taskNames')
    void testTasks(String taskName, boolean runTestTask) {
        def result = gradle.withArguments(taskName, "-is").build()
        assert result.task(":$taskName").outcome in [SUCCESS, UP_TO_DATE]
        if (runTestTask) {
            def testTaskName = 'test' + taskName.capitalize()
            result = gradle.withArguments(testTaskName).build()
            assert result.task(":$taskName").outcome == UP_TO_DATE
            assert result.task(":$testTaskName").outcome == SUCCESS
        }
    }
}
