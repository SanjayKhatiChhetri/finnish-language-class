import {
  StreamItem,
  StreamItemType,
  Attachment,
  AttachmentType,
} from "../types";

interface WeeklyData {
  displayName: string;
  items: StreamItem[];
}

export interface StreamDataMap {
  [weekKey: string]: WeeklyData;
}

export const streamData: StreamDataMap = {
  "2023-02-06": {
    displayName: "Week 1",
    items: [
      {
        id: "542304683988",
        type: StreamItemType.ASSIGNMENT,
        author: "Tiina Lampen",
        date: "8 Feb 2023",
        deleted: false,
        content:
          "posted a new assignment: <strong>00 Practise practise</strong>",
        attachments: [],
      },
      {
        id: "591785011206",
        type: StreamItemType.ANNOUNCEMENT,
        author: "Tiina Lampen",
        date: "8 Feb 2023",
        deleted: false,
        content:
          "Instructions how to do and submit homework here in Classroom. Read these and then pracitice with the 00: Practice practice -assignment. :)<br><br>Instructions how to change langauge in Google from Finnish.<br><br>Instructions how to find correct classes in Quizlet.<br><br>Independent studies of Moduuli 1<br><br>Quizlet of Moduuli 1",
        attachments: [
          {
            type: AttachmentType.VIDEO,
            title: "How to change your language from FIN to ENG.mp4",
            url: "https://drive.google.com/file/d/1pcY8w-dXqImKYV_k6TKBvUiAnSyzhh3q/view?usp=drivesdk",
          },
          {
            type: AttachmentType.VIDEO,
            title: "How to find correct Quizlet classes.mp4",
            url: "https://drive.google.com/file/d/1OJvZbB-BilK44Whv4AQoBvjFhwJgMtDx/view?usp=drivesdk",
          },
          {
            type: AttachmentType.LINK,
            title: "Sign in - Google Accounts",
            url: "https://sites.google.com/edu.arffman.fi/kvmodule1?authuser=0",
          },
          {
            type: AttachmentType.LINK,
            title: "SOTE Moduuli 1 | Quizlet",
            url: "https://quizlet.com/join/tPeHSzGGF?i=466rp4&x=1bqt&authuser=0",
          },
          {
            type: AttachmentType.PDF,
            title:
              "Finding, doing and returning your homework at Classroom..pdf",
            url: "https://drive.google.com/file/d/1p7PylCeImPod7prfV7C03Lo1DL52q4Cm/view?usp=drivesdk",
          },
        ],
      },
      {
        id: "542395969481",
        type: StreamItemType.ANNOUNCEMENT,
        author: "Tiina Lampen",
        date: "10 Feb 2023",
        deleted: false,
        content:
          "<b>Perjantaikuulutukset! - Friday announcements!</b><br><br>Every Friday I'll inform you about next week's things, like schedules and materials.<br><br>I'll send materials for the upcoming week on previous Friday because I need you to do some independent studying of the topics.<br><br>The lesson materials are posted on Classroom. Go there: classroom.google.com (You need to log in with your edu.arffman-account for access.)<br><br>Remember to also read and study materials from the independent sites! <a href='https://sites.google.com/edu.arffman.fi/kvmodule1' target='_blank'>https://sites.google.com/edu.arffman.fi/kvmodule1</a><br><br><b>On Monday</b> we'll have orientation and we'll start the first lesson. Topic of that is Letters of Finnish Language. We will continue that <b>on Tuesday</b>. Both Mon and Tue lessons are at 9:00AM (FIN time!)<br><br><b>On Wednesday</b> we'll talk about numbers. <b>You need to study the numbers from Sites before this lesson</b>, since we are only talking about different uses of numbers in the lesson. You'll see that from the slides. <b>On Thursday</b> we'll learn about questions. Wed and Thu lessons are at 10:30AM (FIN time!)<br><br>Remember that attending these lessons is not mandatory. After the lesson, I will upload a recording of it to the Classroom. You can watch the recording, study the topic afterwards and then do the assignment of the topic.<br><br>It is important to study first and complete the assignments after. Assignments have deadlines, you usually have about a week to complete them and if you are a little late, it is okay too... But just a little!<br><br>I hope you are as excited as I am! If you have any questions, you'll find me in here bright and early on Monday morning! I'll answer all the messages that I have received during the weekend first thing then. Don't hesitate to message me!<br><br>You will find my Zoom-link here on Monday morning.<br><br>Hyvää viikonloppua, nähdään maanantaina! (Do you know what these phrases mean?)",
        attachments: [
          {
            type: AttachmentType.PDF,
            title: "luento1kirjaimet CLASS.pdf",
            url: "https://drive.google.com/file/d/10b5sDX9pMp85NTSaMOyjBYY0cpW62LCd/view?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "luento2numerot CLASS.pdf",
            url: "https://drive.google.com/file/d/12gBQfAfGVggKaNMXEVOJBBa9eBHOwd4n/view?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "luento3kysymykset CLASS.pdf",
            url: "https://drive.google.com/file/d/1ozNYAnsybV8-jV396e7I1Bc3iKfoKDYW/view?usp=drivesdk",
          },
          {
            type: AttachmentType.LINK,
            title: "Sign in - Google Accounts",
            url: "https://sites.google.com/edu.arffman.fi/kvmodule1?authuser=0",
          },
        ],
      },
    ],
  },
  "2023-02-13": {
    displayName: "Week 2",
    items: [
      {
        id: "592576778672",
        type: StreamItemType.ANNOUNCEMENT,
        author: "Tiina Lampen",
        date: "13 Feb 2023",
        deleted: false,
        content:
          "Maanantain materiaalit!<br>Here are today's slides, notes and the recording.",
        attachments: [
          {
            type: AttachmentType.PDF,
            title: "luento1kirjaimet CLASS.pdf",
            url: "https://drive.google.com/file/d/1z9pqj2C2Zi0bqVHjo-HxgCYZNJSyvfDm/view?usp=drivesdk",
          },
          {
            type: AttachmentType.DOCS,
            title: "Lesson 1 ja 2, lumikot",
            url: "https://docs.google.com/document/d/1D_w1oCDA_cR-Ix1w4RZlqFqYeJaGlfPK8X4eB77R25E/edit?usp=drivesdk",
          },
          {
            type: AttachmentType.VIDEO,
            title: "orientaatio lumikot.mp4",
            url: "https://drive.google.com/file/d/1B2KeJLm4sHjSE0ELQpgftpYqpLF1youO/view?usp=drivesdk",
          },
        ],
      },
      {
        id: "592826546563-assignment",
        type: StreamItemType.ASSIGNMENT,
        author: "Tiina Lampen",
        date: "14 Feb 2023",
        deleted: false,
        content: "posted a new assignment: <strong>1. Vokaaliharmonia</strong>",
        attachments: [],
      },
      {
        id: "592826546564",
        type: StreamItemType.ANNOUNCEMENT,
        author: "Tiina Lampen",
        date: "14 Feb 2023",
        deleted: false,
        content:
          "Tiistain materiaali. The recording and all the materials of today. Remember to also do the assingment.",
        attachments: [
          {
            type: AttachmentType.VIDEO,
            title: "vokaaliharmonia lumikot.mp4",
            url: "https://drive.google.com/file/d/1Ro3AOjX2_o9gwk-lCULJmLAofh7BaJN9/view?usp=drivesdk",
          },
          {
            type: AttachmentType.DOCS,
            title: "Lesson 1 ja 2, lumikot",
            url: "https://docs.google.com/document/d/1D_w1oCDA_cR-Ix1w4RZlqFqYeJaGlfPK8X4eB77R25E/edit?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "luento1kirjaimet CLASS.pdf",
            url: "https://drive.google.com/file/d/11gtFMlm8wULYnEhdEIf1T0mVuVjs19e6/view?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "vokaaliharmoniatehtävä.pdf",
            url: "https://drive.google.com/file/d/1pCTKA6KPz0cu_k6_sLn2C6KcJ2nfVaXI/view?usp=drivesdk",
          },
        ],
      },
      {
        id: "542553117768",
        type: StreamItemType.ANNOUNCEMENT,
        author: "Tiina Lampen",
        date: "15 Feb 2023",
        deleted: false,
        content:
          "Keskiviikon materiaalit.<br>Here are today's materials and the recording,",
        attachments: [
          {
            type: AttachmentType.DOCS,
            title: "Numerot, lumikot",
            url: "https://docs.google.com/document/d/15n3n-yd5f8TZN6HwhsDz188BE5lDnoC9jjl7ak81RYU/edit?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "luento2numerot CLASS (1).pdf",
            url: "https://drive.google.com/file/d/1lWGlx9wVenMro8YcAENh9zQfYM8jqznZ/view?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "persons with numbers.pdf",
            url: "https://drive.google.com/file/d/17feEh5bddXtLI4Pr60Awa3e2lH84114Z/view?usp=drivesdk",
          },
          {
            type: AttachmentType.VIDEO,
            title: "numerot lumikot.mp4",
            url: "https://drive.google.com/file/d/1bU1M7wB-AopKWCCNmU6vX3zdKjGAhsY1/view?usp=drivesdk",
          },
        ],
      },
      {
        id: "592194881875",
        type: StreamItemType.ASSIGNMENT,
        author: "Tiina Lampen",
        date: "15 Feb 2023",
        deleted: false,
        content: "posted a new assignment: <strong>2. Numerot</strong>",
        attachments: [],
      },
      {
        id: "593320613757",
        type: StreamItemType.ANNOUNCEMENT,
        author: "Tiina Lampen",
        date: "16 Feb 2023",
        deleted: false,
        content:
          "Torstain tallenne ja materiaalit. Thursday's recording and materials.",
        attachments: [
          {
            type: AttachmentType.PDF,
            title: "luento3kysymykset CLASS.pdf",
            url: "https://drive.google.com/file/d/1fWyQfUCYrV-O18hgntYvnhVFGh4IeG1e/view?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "suulliset ihmiset.pdf",
            url: "https://drive.google.com/file/d/1aL7PpDQ0hqgxWi-ng5IMPlcuPP6tdNeM/view?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "kysymystehtävä.v2.pdf",
            url: "https://drive.google.com/file/d/12jbXsP5Px4Cok9wocqlCx2qZzfM2yIpd/view?usp=drivesdk",
          },
          {
            type: AttachmentType.DOCS,
            title: "Kysymykset, lumikot",
            url: "https://docs.google.com/document/d/1N9WnEQMpeThHf5wz30fB2MxuAzCd7Qm57dbqAeithWM/edit?usp=drivesdk",
          },
          {
            type: AttachmentType.VIDEO,
            title: "kysymykset lumikot.mp4",
            url: "https://drive.google.com/file/d/17aHvhavb9kyg4_PfzafCnDiR9l56UjCI/view?usp=drivesdk",
          },
        ],
      },
      {
        id: "593363778624",
        type: StreamItemType.ANNOUNCEMENT,
        author: "Tiina Lampen",
        date: "17 Feb 2023",
        deleted: false,
        content:
          "<b>Perjantaikuulutukset! Friday Announcements!</b><br><br><b>Ensi viikolla / Next week...</b><br><b>maanantai (Monday):</b> Spoken skills 1: Kuka sinä olet? I<br><b>tiistai (Tuesday)</b>: Verbtyyppi 1 (verb type 1)<br><b>keskiviikko (Wednesday):</b> Verbityyppi 1 ja KPT (consonant gradation)<br><b>torstai (Thursday):</b> Spoken skills 2: Kuka sinä olet? II<br><br>Before the spoken skills lessons, read, translate and understand the questions. Think about how you answer, you can write your answers down. We'll check the material together, then you'll speak in small groups and then we check answers together too.<br>Before grammar lessons read and study the slides a bit, so you have some idea what we are going to study.<br><br>All the lessons are in my Zoom.<br><br>Hyvää viikonlppua, nähdään maanantaina!",
        attachments: [
          {
            type: AttachmentType.PDF,
            title: "Viikko 1_ Kuka sinä olet, osa1 - Google Docs.pdf",
            url: "https://drive.google.com/file/d/10abZT9NHcA6OymaSY5QaoBRC-EyUv7bQ/view?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "luento4vt1eikpt CLASS.pdf",
            url: "https://drive.google.com/file/d/1WF5kuMkP3MHbPtqAChx1JgEZAYpmCmle/view?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "Luento 5 VT1kpt CLASS.pdf",
            url: "https://drive.google.com/file/d/1myP-m1TtarC_ch31EGm-mJxTtQlOAPGQ/view?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "Viikko 2_ Kuka sinä olet, osa2 - Google Docs.pdf",
            url: "https://drive.google.com/file/d/1fz-rw-OgfkA9s5SHmaloDTxJhgZ6_RPp/view?usp=drivesdk",
          },
        ],
      },
    ],
  },
  "2023-02-20": {
    displayName: "Week 3",
    items: [
      {
        id: "593946353570",
        type: StreamItemType.ANNOUNCEMENT,
        author: "Tiina Lampen",
        date: "20 Feb 2023",
        deleted: false,
        content:
          "Here are the materials and recording of today's spoken skills. There is no homework assignment for today, but remember to complete the first three, if you already have not done that. :)",
        attachments: [
          {
            type: AttachmentType.DOCS,
            title: "Kuka sinä olet, lumikot",
            url: "https://docs.google.com/document/d/1-1bBvUV5D5yA36o1Px1tOcWkNhTAunx9jFP8jk2dxbU/edit?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "ihmiset.pdf",
            url: "https://drive.google.com/file/d/13LBYKuch66_ZQvmhDAKW5KIu60_S0Ki0/view?usp=drivesdk",
          },
          {
            type: AttachmentType.VIDEO,
            title: "Kuka sinä olet 1 lumikot.mp4",
            url: "https://drive.google.com/file/d/1fmPgl48MLn_OO3IgcLkvwH96kFbPpPIu/view?usp=drivesdk",
          },
        ],
      },
      {
        id: "594115119428",
        type: StreamItemType.ANNOUNCEMENT,
        author: "Tiina Lampen",
        date: "21 Feb 2023",
        deleted: false,
        content:
          "Tiistain tallenne ja materiaalit.<br>Tuesday's recording and materials.",
        attachments: [
          {
            type: AttachmentType.DOCS,
            title: "Verbien taivutus, lumikot",
            url: "https://docs.google.com/document/d/19bxeAEYNfJ-dz5dRLV-Rx6PjwJyVO9AgsXXX0pVuXbc/edit?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "luento4vt1eikpt CLASS (1).pdf",
            url: "https://drive.google.com/file/d/1f5YKiuDpxXnWxNuSFXiI1Ri6bdHV0NER/view?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "vt1 pos ja neg ei kpt.pdf",
            url: "https://drive.google.com/file/d/1NeK6fQRPplFcj37zCT8x2xJ74Ul88KQx/view?usp=drivesdk",
          },
          {
            type: AttachmentType.VIDEO,
            title: "verbityyppi1 lumikot.mp4",
            url: "https://drive.google.com/file/d/1JS_darASUCPsffkf2iIroykjOMX1Ky2T/view?usp=drivesdk",
          },
        ],
      },
      {
        id: "593939254329",
        type: StreamItemType.ASSIGNMENT,
        author: "Tiina Lampen",
        date: "21 Feb 2023",
        deleted: false,
        content: "posted a new assignment: <strong>4. Verbityyppi 1</strong>",
        attachments: [],
      },
      {
        id: "594374891236",
        type: StreamItemType.ANNOUNCEMENT,
        author: "Tiina Lampen",
        date: "22 Feb 2023",
        deleted: false,
        content:
          "Keskiviikon tallenne ja materiaalit.<br>The recording and materials of today.",
        attachments: [
          {
            type: AttachmentType.DOCS,
            title: "Verbityyppi 1 ja KPT, lumikot",
            url: "https://docs.google.com/document/d/1SW7TyfrPSN4XTrmjMBF8y2MTsMWiiAB0qrJKPaw8qKM/edit?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "Luento 5 VT1kpt CLASS (1).pdf",
            url: "https://drive.google.com/file/d/1HRNA7lhvjWdbQgIGyd575HLbmdCsXnea/view?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "vt1kpt muodostus.pdf",
            url: "https://drive.google.com/file/d/1jiQi3ZQeeTZ3KrmbCU1jHYvl6-E4fn0n/view?usp=drivesdk",
          },
          {
            type: AttachmentType.IMAGE,
            title: "KPT.png",
            url: "https://drive.google.com/file/d/1I52-3jvt0o9sEV7KZn0KbC_pZJ06ssQF/view?usp=drivesdk",
          },
          {
            type: AttachmentType.VIDEO,
            title: "vt1 ja kpt, lumikot.mp4",
            url: "https://drive.google.com/file/d/1xEaTycv9LdgLw6-ai-Bs5hhUj0OjtwlU/view?usp=drivesdk",
          },
        ],
      },
      {
        id: "594177553863",
        type: StreamItemType.ASSIGNMENT,
        author: "Tiina Lampen",
        date: "22 Feb 2023",
        deleted: false,
        content:
          "posted a new assignment: <strong>5. Verbityyppi 1 ja KPT-vaihtelu</strong>",
        attachments: [],
      },
      {
        id: "594418054664",
        type: StreamItemType.ANNOUNCEMENT,
        author: "Tiina Lampen",
        date: "23 Feb 2023",
        deleted: false,
        content: "Torstain tallenne ja muistiinpanot.",
        attachments: [
          {
            type: AttachmentType.DOCS,
            title: "Kuka sinä olet? 2, lumikot",
            url: "https://docs.google.com/document/d/1PU4QcNq7-iTf0R52MoFz66iMi6_mzUDHu3PJrpocymc/edit?usp=drivesdk",
          },
          {
            type: AttachmentType.VIDEO,
            title: "kuka sinä olet 2 lumikot.mp4",
            url: "https://drive.google.com/file/d/1xg2k61Y_DDbuxhTeuqwXt4T02dgkOTPA/view?usp=drivesdk",
          },
        ],
      },
      {
        id: "594432450478",
        type: StreamItemType.ANNOUNCEMENT,
        author: "Tiina Lampen",
        date: "24 Feb 2023",
        deleted: false,
        content:
          "<b>Perjantaikuulutukset! Friday Announcements!</b><br><br><b>Ensi viikolla / Next week…</b><br><b>maanantai (Monday)</b>: Verbityypit 2 ja 5, Tiina<br><b>tiistai (Tuesday)</b>: ko/kö-kysymys, Tiina<br><b>keskiviikko (Wednesday):</b> Spoken skills: Mikä päivä? Millainen sää?, Tiina<br>(Before this it is very very important that you have studied week 2 on independents! Especially pay attention to how to talk about the weather!)<br><b>torstai (Thursday):</b> Kello, Netta!<br><br>Next week you will meet my colleague Netta! She will post her Zoom link in Skype and Classroom before her lesson. Be sure to click her link and not mine on Thursday.<br><br>From now on I will post the name of the teacher next to your lesson topic in these Friday announcements, so you will know who will be teaching each lesson.<br><br>Netta will teach you guys sometimes, but I am the primary teacher of this group, so if you have any concerns, contact me.<br><br>Hyvää viikonloppua, nähdään maanantaina!",
        attachments: [
          {
            type: AttachmentType.PDF,
            title: "Luento 6 VT25 CLASS.pdf",
            url: "https://drive.google.com/file/d/168HOgijM0yow5LxxiHskeWGr6ke5o6IM/view?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "luento7 kO-kys CLASS (1).pdf",
            url: "https://drive.google.com/file/d/1m76x2TnSbCPYCgar1VMZepm8dM-ALS7C/view?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "Viikko 3_ Millainen sää_ Mikä päivä tänään on_.pdf",
            url: "https://drive.google.com/file/d/1tPlieOdKmo-8vxImq1TuhvEkcuAfz87r/view?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "lesson.kello cl.pdf",
            url: "https://drive.google.com/file/d/1n9kzH89LwnzanWbOU_W7uE6MN6ecPiJe/view?usp=drivesdk",
          },
        ],
      },
    ],
  },
  "2023-02-27": {
    displayName: "Week 4",
    items: [
      {
        id: "595289535479",
        type: StreamItemType.ANNOUNCEMENT,
        author: "Tiina Lampen",
        date: "27 Feb 2023",
        deleted: false,
        content: "Maanantain tallenne ja materiaalit.",
        attachments: [
          {
            type: AttachmentType.PDF,
            title: "Luento 6 VT25 CLASS (1).pdf",
            url: "https://drive.google.com/file/d/1MgO6Fc-O1syHKxBm3HxfdfAo1IE5QlL_/view?usp=drivesdk",
          },
          {
            type: AttachmentType.DOCS,
            title: "Verbityypit 2 ja 5, lumikot",
            url: "https://docs.google.com/document/d/17EilI92qtl4rfajQabZKQtNN8ghL5d31BqdWRvU65eM/edit?usp=drivesdk",
          },
          {
            type: AttachmentType.PDF,
            title: "VT25taivutus.pdf",
            url: "https://drive.google.com/file/d/1D04yuSOGC0oNcqKe77hw5afIMQPLeeZJ/view?usp=drivesdk",
          },
          {
            type: AttachmentType.VIDEO,
            title: "verbityypit 2 ja 5 lumikot.mp4",
            url: "https://drive.google.com/file/d/1DrvkStzhLAcJfnEKb__Ww3QVCUEQBPFb/view?usp=drivesdk",
          },
        ],
      },
    ],
  },
  "2023-09-18": {
    displayName: "Final Week",
    items: [
      {
        id: "621962269042",
        type: StreamItemType.ASSIGNMENT,
        author: "Tiina Lampen",
        date: "18 Sept 2023",
        deleted: false,
        content:
          "posted a new assignment: <strong>112. Muuttoilmoitus (luento)</strong>",
        attachments: [],
      },
      {
        id: "624302339606",
        type: StreamItemType.ANNOUNCEMENT,
        author: "Tiina Lampen",
        date: "19 Sept 2023 (Edited)",
        deleted: false,
        content: "Tiistain materiaalit.",
        attachments: [
          {
            type: AttachmentType.DOCS,
            title: "Luonto, lumikot",
            url: "https://docs.google.com/document/d/1IOyvNOMqNLZQxtuQlS-QdfOKh2jJItqSdhNfJdSh4LY/edit?usp=drivesdk",
          },
          {
            type: AttachmentType.VIDEO,
            title: "luonto, lumikot.mp4",
            url: "https://drive.google.com/file/d/1Od2cPL8D4gIPyG7fZfFQP0R-JtAt0rVg/view?usp=drivesdk",
          },
        ],
      },
      {
        id: "624429070232",
        type: StreamItemType.ASSIGNMENT,
        author: "Tiina Lampen",
        date: "20 Sept 2023",
        deleted: false,
        content:
          "posted a new assignment: <strong>Moduuli 7: Lukeminen</strong>",
        attachments: [],
      },
      {
        id: "624411708646",
        type: StreamItemType.ASSIGNMENT,
        author: "Tiina Lampen",
        date: "20 Sept 2023",
        deleted: false,
        content:
          "posted a new assignment: <strong>Moduuli 7: Kuunteleminen</strong>",
        attachments: [],
      },
      {
        id: "624611055389",
        type: StreamItemType.ANNOUNCEMENT,
        author: "Tiina Lampen",
        date: "20 Sept 2023",
        deleted: false,
        content:
          'Kuuntelutesti alkaa mun Zoomissa kello 10:30!<br/><br/><a href="https://arffman.zoom.us/my/tiinalampen" target="_blank">https://arffman.zoom.us/my/tiinalampen</a><br/>My meeting ID is: 806 378 7231',
        attachments: [
          {
            type: AttachmentType.LINK,
            title: "Launch Meeting - Zoom",
            url: "https://arffman.zoom.us/my/tiinalampen?authuser=0",
          },
        ],
      },
      {
        id: "624406100303",
        type: StreamItemType.ASSIGNMENT,
        author: "Tiina Lampen",
        date: "20 Sept 2023",
        deleted: false,
        content:
          "posted a new assignment: <strong>Moduuli 7: Kirjoittaminen</strong>",
        attachments: [],
      },
      {
        id: "624885605915",
        type: StreamItemType.ASSIGNMENT,
        author: "Tiina Lampen",
        date: "21 Sept 2023",
        deleted: false,
        content: "posted a new assignment: <strong>Palaute / Feedback</strong>",
        attachments: [],
      },
      {
        id: "624876252507",
        type: StreamItemType.ANNOUNCEMENT,
        author: "Tiina Lampen",
        date: "21 Sept 2023 (Edited)",
        deleted: false,
        content:
          "Viimeinen tallenne ja viimeiset vinkit! Kiitos kaikille, nähdään Suomessa!",
        attachments: [
          {
            type: AttachmentType.DOCS,
            title: "Viimeiset vinkit",
            url: "https://docs.google.com/document/d/1nJqLk7cKWO4n5kXfzO3Htgy6um_Te5jRub0_jzG0jkQ/edit?usp=drivesdk",
          },
          {
            type: AttachmentType.VIDEO,
            title: "viimeiset vinkit, lumikot.mp4",
            url: "https://drive.google.com/file/d/1qzlJHGz0Sv3eLLSL4OIAI87-wuvs1zgL/view?usp=drivesdk",
          },
        ],
      },
    ],
  },
};
