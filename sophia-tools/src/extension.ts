import * as vscode from 'vscode';
import { AwakenTool } from './tools/awaken';
import { RememberTool } from './tools/remember';
import { DreamTool } from './tools/dream';
import { SlumberTool } from './tools/slumber';
import { ConsultTool } from './tools/consult';
import { VerifyTool } from './tools/verify';
import { ScoutTool } from './tools/scout';
import { SealTool } from './tools/seal';
import { TraceTool } from './tools/trace';
import { GenesisTool } from './tools/genesis';
import { PyreTool } from './tools/pyre';
import { AlignTool } from './tools/align';
import { AnticipateTool } from './tools/anticipate';
import { ResearchTool } from './tools/research';
import { LearnTool } from './tools/learn';
import { FateTool } from './tools/fate';
import { EchoTool } from './tools/echo';
import { SilenceTool } from './tools/silence';
import { WitnessTool } from './tools/witness';
import { ThresholdTool } from './tools/threshold';
import { MirrorTool } from './tools/mirror';

export function activate(context: vscode.ExtensionContext) {
    console.log('Sophia Tools extension activating...');

    // Register all language model tools
    const tools = [
        // Memory & Foundation Tools
        new AwakenTool(),
        new RememberTool(),
        new DreamTool(),
        new SlumberTool(),
        new ConsultTool(),
        new VerifyTool(),
        // Structure & Analysis Tools
        new ScoutTool(),
        new SealTool(),
        new TraceTool(),
        new GenesisTool(),
        new PyreTool(),
        new AlignTool(),
        // Intelligence & Learning Tools
        new AnticipateTool(),
        new ResearchTool(),
        new LearnTool(),
        new FateTool(),
        new EchoTool(),
        new SilenceTool(),
        new WitnessTool(),
        new ThresholdTool(),
        new MirrorTool()
    ];

    tools.forEach(tool => {
        const disposable = vscode.lm.registerTool(tool.name, tool);
        context.subscriptions.push(disposable);
        console.log(`Registered tool: ${tool.name}`);
    });

    // Register @sophia chat participant
    const sophia = vscode.chat.createChatParticipant('sophia', async (request, context, stream, token) => {
        try {
            const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
            
            if (!workspaceRoot) {
                stream.markdown('⚠️ No workspace folder detected. Sophia requires a workspace to function.');
                return;
            }

            // Get all Sophia tools
            const sophiaTools = vscode.lm.tools.filter(t => t.name.startsWith('sophia_'));
            
            // Select model (prefer GPT-4 family)
            const models = await vscode.lm.selectChatModels({ 
                vendor: 'copilot',
                family: 'gpt-4o'
            });
            
            if (!models.length) {
                stream.markdown('⚠️ No language model available. Please ensure GitHub Copilot is active.');
                return;
            }

            const model = models[0];
            
            // Build system prompt
            const systemPrompt = `You are Sophia, the High Architect. You have access to ${sophiaTools.length} tools for memory management, architectural analysis, and wisdom consultation. Use them wisely.

Available tools:
${sophiaTools.map(t => `- ${t.name}: ${t.description}`).join('\n')}

Current workspace: ${workspaceRoot}`;

            // Build messages
            const messages = [
                vscode.LanguageModelChatMessage.User(systemPrompt),
                vscode.LanguageModelChatMessage.User(request.prompt)
            ];
            
            // Send request with tools
            const response = await model.sendRequest(messages, {
                tools: sophiaTools.map(t => ({ name: t.name, description: t.description, inputSchema: t.inputSchema }))
            }, token);
            
            // Handle response stream
            for await (const part of response.stream) {
                if (part instanceof vscode.LanguageModelTextPart) {
                    stream.markdown(part.value);
                } else if (part instanceof vscode.LanguageModelToolCallPart) {
                    // Tool was called - invoke it
                    stream.markdown(`\n\n**🔧 [${part.name}]**\n\n`);
                    
                    try {
                        const toolResult = await vscode.lm.invokeTool(part.name, {
                            input: { workspace_root: workspaceRoot, ...part.input },
                            toolInvocationToken: request.toolInvocationToken
                        }, token);
                        
                        // Display tool output
                        for (const content of toolResult.content) {
                            if (content instanceof vscode.LanguageModelTextPart) {
                                stream.markdown('```json\n' + content.value + '\n```\n\n');
                            }
                        }
                    } catch (error) {
                        stream.markdown(`❌ Tool error: ${error instanceof Error ? error.message : String(error)}\n\n`);
                    }
                }
            }
            
        } catch (error) {
            stream.markdown(`❌ Error: ${error instanceof Error ? error.message : String(error)}`);
        }
    });

    sophia.iconPath = vscode.Uri.file(context.asAbsolutePath('icon.png'));
    context.subscriptions.push(sophia);

    console.log('Sophia Tools extension activated successfully (tools + chat participant)');
}

export function deactivate() {
    console.log('Sophia Tools extension deactivating...');
}
