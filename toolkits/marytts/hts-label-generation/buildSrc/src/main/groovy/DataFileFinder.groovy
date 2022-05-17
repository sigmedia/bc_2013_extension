// package de.dfki.mary.htsvoicebuilding

import groovy.json.* // To load the JSON configuration file

public class DataFileFinder {
    def static project_path

    static File getFilePath(String filename) {
        // Absolute path
        if (filename.startsWith("/")){
            return new File(filename)
        }


        return new File(project_path, filename)
    }

    static File getFilePath(String filename, String ext) {
        if (ext.startsWith(".")){
            return getFilePath(filename + ext)
        }

        return getFilePath(filename + "." + ext)
    }
}
