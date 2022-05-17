package marytts.tasks

import org.gradle.api.DefaultTask
import org.gradle.api.file.DirectoryProperty
import org.gradle.api.file.RegularFileProperty
import org.gradle.api.provider.Property
import org.gradle.api.tasks.*

// MaryTTS
import marytts.io.serializer.Serializer
import marytts.io.serializer.ROOTSJSONSerializer
import marytts.data.Utterance
import marytts.data.Sequence
import marytts.data.Relation
import marytts.data.item.acoustic.Segment
import marytts.data.item.phonology.Phoneme
import marytts.data.item.phonology.NSS
import marytts.data.SupportedSequenceType

// TextGrid
import org.m2ci.msp.jtgt.*
import org.m2ci.msp.jtgt.io.*


class AddDurationToUtt extends DefaultTask {

    @Input
    final Property<String> phTierName = project.objects.property(String)

    @InputDirectory
    final DirectoryProperty srcTextGridDir = project.objects.directoryProperty()

    @InputDirectory
    final DirectoryProperty srcUttDir = project.objects.directoryProperty()

    @OutputDirectory
    final DirectoryProperty destUttDir = project.objects.directoryProperty()

    @TaskAction
    void merge() {

        // Call Mary
        def dict = [:]
        project.fileTree(srcUttDir).include('*.json').collect { inUttFile ->
            try {
                // Get original Utt
                Serializer ser = new ROOTSJSONSerializer();
                Utterance utt = ser.load(inUttFile.text)

                // Get Textgrid based Utt
                TextGrid tg = new TextGridSerializer().fromString(
                    srcTextGridDir.file(inUttFile.name - '.json' + '.TextGrid').get().asFile.text
                )

                // Find the accurate tier
                Tier ph_tier = null
                for (Tier t: tg.getTiers()) {
                    if (t.getName() == phTierName.get()) {
                        ph_tier = t;
                        break;
                    }
                }

                // Count the number of phonemes from the textgrid
                ArrayList<Annotation> tgt_segments = ph_tier.getAnnotations()
                int nb_ph
                for (int i=0; i<tgt_segments.size(); i++) {
                    Annotation tmp = tgt_segments.get(i);
                    if ((tmp.getText() != "") &&
                        (tmp.getText() != "sil") &&
                        (tmp.getText() != "sp"))
                    {
                        nb_ph += 1
                    }
                }

                // Count the number of phones from the utterance file
                Sequence<Phoneme> phonemes = (Sequence<Phoneme>) utt.getSequence(SupportedSequenceType.PHONE)
                if (phonemes.size() != nb_ph) {
                    String tmp = "";
                    for (int i=0; i<phonemes.size(); i ++) {
                        tmp += phonemes.get(i).toString() + ", "
                    }
                    project.logger.debug("src part: " + tmp);

                    tmp = "";
                    for (int i=0; i<tgt_segments.size(); i ++) {
                        if ((tgt_segments.get(i).getText() != "") &&
                            (tgt_segments.get(i).getText() != "sil") &&
                            (tgt_segments.get(i).getText() != "sp"))
                        {
                            tmp += tgt_segments.get(i).getText() + ", "
                        }
                    }
                    project.logger.debug("tgt part: " + tmp);
                    throw new Exception(String.format("(Phone) utt segs (%d) != tgt segs (%d)", phonemes.size(), nb_ph))
                }

                // Merge Utts
                Sequence<Segment> segments = (Sequence<Segment>) utt.getSequence(SupportedSequenceType.SEGMENT)
                Sequence<NSS> nss = (Sequence<NSS>) utt.getSequence(SupportedSequenceType.NSS)

                Relation rel_ph = utt.getRelation(SupportedSequenceType.SEGMENT, SupportedSequenceType.PHONE)
                Relation rel_nss = utt.getRelation(SupportedSequenceType.SEGMENT, SupportedSequenceType.NSS)

                int an_offset = 0
                int nss_index = 0
                for (int i=0; i<tgt_segments.size(); i++) {
                    Annotation an = tgt_segments[i]

                    // Ignore last blank if necessary!
                    if ((i-an_offset) >= segments.size() &&
                        (i == (tgt_segments.size()-1)) &&
                        (an.getText() == "")) {
                        project.logger.debug("ok ignore !");
                        continue;
                    }

                    // Get Phone sequence
                    project.logger.debug("an = " + an.getText());
                    Phoneme[] seg_ph = (Phoneme[]) rel_ph.getRelatedItems(i-an_offset)
                    if (seg_ph.size() > 0) {
                        project.logger.debug(String.format("related phone = %s", seg_ph.toString()));
                    }

                    // Get NSS Sequence
                    NSS[] seg_nss = (NSS[]) rel_nss.getRelatedItems(i-an_offset)
                    if (seg_nss.size() > 0) {
                        project.logger.debug(String.format("related nss = %s", seg_nss.toString()));
                    }

                    // Phone
                    if ((an.getText() != "") &&
                        (an.getText() != "sil") &&
                        (an.getText() != "sp"))
                    {
                        Phoneme[] segments_ph = (Phoneme[]) rel_ph.getRelatedItems(i-an_offset)

                        // Normal scenario: phone related to one and only on phone
                        if (segments_ph.size() == 1) {
                            Segment s = segments[i-an_offset]
                            s.setStart(an.getStart()*1000)
                            s.setDuration(an.getEnd()*1000 - an.getStart()*1000)
                        }

                        // On the sequence side => it should be an NSS
                        else if (segments_ph.size() == 0) {
                            int[] segments_nss = rel_nss.getRelatedIndexes(i-an_offset)
                            if (segments_nss.size() != 1) {
                                throw new Exception("Invalid number of NSS (${segments_nss.size()}) associated to the index (${i-an_offset})")
                            }
                            nss_index = segments_nss[0]
                            nss.remove(nss_index)
                            segments.remove(i-an_offset)
                            an_offset += 1
                        }

                        // annotation related to too many phones
                        else {
                            throw new Exception(String.format("Segment %d is related to %d phones (> 1), which is invalid!", i-an_offset, segments_ph.size()))
                        }
                    }

                    // Error (unknown token)
                    else if (an.getText() == "spn") {
                        throw new Exception(String.format("Segment %d is related to an unknown token!", i-an_offset, segments.size()))
                    }

                    // NSS
                    else {
                        NSS[] segments_nss = (NSS[]) rel_nss.getRelatedItems(i-an_offset)


                        // Normal scenario: NSS related to a NSS
                        if (segments_nss.size() == 1) {
                            Segment s = segments[i-an_offset]
                            s.setStart(an.getStart()*1000)
                            s.setDuration(an.getEnd()*1000 - an.getStart()*1000)
                        }

                        // On the sequence side => we add an nss
                        else if (segments_nss.size() == 0) {
                            NSS tmp_nss = new NSS(an.getText())
                            nss.add(nss_index, tmp_nss)

                            Segment s = new Segment(an.getStart()*1000, an.getEnd()*1000 - an.getStart()*1000)
                            segments.add(i-an_offset, s)
                            rel_nss.addRelation(i-an_offset, nss_index)
                        }

                        // Annotations related to too many NSS
                        else {
                            throw new Exception(String.format("Segment %d is related to %d NSS, which is invalid!", i-an_offset, segments_nss.size()))
                        }

                        nss_index += 1
                    }
                }

                // utt.addSequence(SupportedSequenceType.NSS, nss);
                // utt.setRelation(SupportedSequenceType.SEGMENT, SupportedSequenceType.PHONE, rel_ph);

                // FIXME: update the relation as we have the reverse. Check if native!
                utt.setRelation(SupportedSequenceType.NSS, SupportedSequenceType.SEGMENT, rel_nss.getReverse());

                // Apply dedicated serializer and save the UTT
                def output = ser.export(utt);
                destUttDir.file(inUttFile.name).get().asFile.withWriter('UTF-8') { out ->
                    out.println output
                }
            } catch (FileNotFoundException ex) {
                project.logger.error "Excluding $inUttFile.name during duration alignment: ${ex}" // FIXME: more detail message
            }
        }
    }
}
