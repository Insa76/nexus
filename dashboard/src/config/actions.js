export const ACTIONS = {

  // =========================
  // CREATE FOLDER
  // =========================
  create_folder: {

    label: "Crear carpeta",

    fields: [
      {
        name: "path",
        label: "Ruta",
        type: "text"
      }
    ]
  },

  // =========================
  // MOVE FILES
  // =========================
  move_files: {

    label: "Mover archivos",

    fields: [
      {
        name: "ext",
        label: "Extensión",
        type: "text"
      },
      {
        name: "to",
        label: "Destino",
        type: "text"
      }
    ]
  },

  // =========================
  // OPEN URL
  // =========================
  open_url: {

    label: "Abrir URL",

    fields: [
      {
        name: "url",
        label: "URL",
        type: "text"
      }
    ]
  },

  // =========================
  // IF EXTENSION
  // =========================
  if_extension: {

    label: "IF Extension",

    fields: [
      {
        name: "ext",
        label: "Extension",
        type: "text"
      }
    ]
  },

  join: {
  label: "JOIN",
  fields: []
},

approval: {
  label: "Human Approval",
  fields: [
    {
      name: "message",
      label: "Approval Message"
    }
  ]
},

ai_classify_file: {

  label: "AI Classify File",

  fields: [
    {
      name: "prompt",
      label: "AI Prompt"
    }
  ]
},

ai_agent: {

  label: "AI Agent",

  fields: [

    {
      name: "prompt",
      label: "Prompt"
    },

    {
      name: "model",
      label: "Model"
    }
  ]
},

ai_tool_agent: {

  label: "AI Tool Agent",

  fields: [

    {
      name: "goal",
      label: "Goal"
    },

    {
      name: "model",
      label: "Model"
    }
  ]
},

ai_autonomous_agent: {

  label: "Autonomous AI Agent",

  fields: [

    {
      name: "goal",
      label: "Goal"
    },

    {
      name: "model",
      label: "Model"
    },

    {
      name: "max_steps",
      label: "Max Steps"
    }
  ]
},

ai_generate_workflow: {

  label: "AI Generate Workflow",

  fields: [

    {
      name: "goal",
      label: "Goal"
    },

    {
      name: "model",
      label: "Model"
    }
  ]
},

click: {

  label: "Mouse Click",

  fields: [

    {
      name: "x",
      label: "X"
    },

    {
      name: "y",
      label: "Y"
    }
  ]
},

type_text: {

  label: "Type Text",

  fields: [

    {
      name: "text",
      label: "Text"
    }
  ]
},

screenshot: {

  label: "Screenshot",

  fields: []
},

vision_read: {

  label: "Vision Read",

  fields: []
},

ai_vision_agent: {

  label: "AI Vision Agent",

  fields: [

    {
      name: "goal",
      label: "Goal"
    }
  ]
},

vision_click: {

  label: "Vision Click",

  fields: [

    {
      name: "target",
      label: "Target Text"
    }
  ]
},

visual_autonomous_agent: {

  label: "Visual Autonomous Agent",

  fields: [

    {
      name: "goal",
      label: "Goal"
    }
  ]
},

detect_objects: {

  label: "Detect Objects",

  fields: []
},

ai_visual_reasoning: {

  label: "AI Visual Reasoning",

  fields: [

    {
      name: "goal",
      label: "Goal"
    }
  ]
},

list_ui: {

  label: "List UI Elements",

  fields: []
},

focus_window: {

  label: "Focus Window",

  fields: [

    {
      name: "title",
      label: "Window Title"
    }
  ]
},



};