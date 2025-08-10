
import { GoogleGenAI, Type } from "@google/genai";
import { StreamItem, Summary, LearnMore } from '../types';

if (!process.env.API_KEY) {
    console.warn("API_KEY environment variable not set. AI features will not work.");
}

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY! });

const summarySchema = {
    type: Type.OBJECT,
    properties: {
      title: {
        type: Type.STRING,
        description: "A concise, high-level summary title for the provided week's content. For example: 'Week of 2023-09-18: Final Tests & Project Work'."
      },
      keyPoints: {
        type: Type.ARRAY,
        description: "An array of strings, where each string is a key takeaway or important announcement from the stream for that week. Focus on the most critical information.",
        items: { type: Type.STRING }
      },
      upcomingAssignments: {
        type: Type.ARRAY,
        description: "An array of objects for all items of type 'ASSIGNMENT' within the given week.",
        items: {
          type: Type.OBJECT,
          properties: {
            title: {
              type: Type.STRING,
              description: "The title of the assignment."
            },
            dueDate: {
              type: Type.STRING,
              description: "The due date for the assignment. If not specified, return 'No due date mentioned'."
            }
          },
          required: ["title", "dueDate"]
        }
      }
    },
    required: ["title", "keyPoints", "upcomingAssignments"]
};


export const generateStreamSummary = async (items: StreamItem[], weekTitle: string): Promise<Summary> => {
  const simplifiedItems = items.map(item => ({
    type: item.type,
    author: item.author,
    date: item.date,
    content: item.content.replace(/\*\*|\*/g, '').substring(0, 300),
    attachments: item.attachments.map(a => a.title),
  }));

  const prompt = `
    Analyze the following JSON data representing posts from a Google Classroom course for the ${weekTitle}. The primary language of the course materials is Finnish.
    
    Generate a concise summary in English. The summary must include:
    1. A main title for the summary of the week.
    2. A few key points highlighting the most important topics or announcements from the posts.
    3. A list of all assignments mentioned in this week's stream, including their titles and due dates. If a due date isn't mentioned, state "No due date mentioned".
    
    Return the response ONLY in the specified JSON format.

    Classroom Stream Data for the Week:
    ${JSON.stringify(simplifiedItems, null, 2)}
  `;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: summarySchema,
      }
    });
    
    const responseText = (response as any).text;
    if (!responseText || typeof responseText !== 'string') {
      throw new Error("Invalid response from Gemini API");
    }
    const text = responseText.trim();
    return JSON.parse(text) as Summary;

  } catch (error) {
    console.error("Error generating summary with Gemini:", error);
    throw new Error("Failed to parse summary from Gemini API.");
  }
};


export const learnMoreAbout = async (topic: string, contextItems: StreamItem[]): Promise<LearnMore> => {
    const simplifiedContext = contextItems.map(item => ({
        content: item.content.replace(/\*\*|\*/g, '').substring(0, 200),
        attachments: item.attachments.map(a => a.title),
    })).slice(0, 5);

    const prompt = `
        A student studying a Finnish language course is asking to learn more about the topic: "${topic}".
        The context of their course for this week includes the following items:
        ${JSON.stringify(simplifiedContext, null, 2)}

        Please provide a clear and concise explanation of "${topic}" in English, suitable for a language learner.
        - Start with a clear definition.
        - Use bullet points for key aspects or rules if applicable.
        - Provide simple examples in Finnish with English translations.
        - Keep it focused and easy to understand.
        - Format the entire response in Markdown.
    `;
    
    const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: prompt,
    });

    return {
        title: `Learn More: ${topic}`,
        explanation: response.text || 'No explanation available',
    };
};
