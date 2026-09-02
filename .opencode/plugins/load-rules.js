// Project-local OpenCode plugin: asks the agent to load workshop rules on session start.
export const LoadRules = async ({ client }) => {
  return {
    event: async ({ event }) => {
      if (event.type === "session.start") {
        await client.session.prompt({
          parts: [{
            type: "text",
            text: "Прочитай корневой AGENTS.md перед началом работы. Он сам укажет, какие .agents/* правила и skills нужны под задачу.",
          }],
        });
      }
    },
  };
};
