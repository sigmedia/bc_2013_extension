plugins {
    `kotlin-dsl`
}

repositories {
    jcenter()
    mavenLocal()
}

val maryttsVersion: String = "6.0.2-SNAPSHOT"

dependencies {
    compile(group="org.apache.logging.log4j", name="log4j-core", version="2.9.1")
    compile(group="de.dfki.mary", name="marytts-runtime", version=maryttsVersion)
    compile(group="de.dfki.mary", name="marytts-lang-en", version=maryttsVersion)
    compile(group="de.dfki.mary", name="marytts-lang-de", version=maryttsVersion)
}
