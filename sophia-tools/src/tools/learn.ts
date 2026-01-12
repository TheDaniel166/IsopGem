import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface LearnInput {
    workspace_root: string;
    event_type: string;
    event_data: string;
}

export interface LearnResult {
    event_type: string;
    recorded: boolean;
    patterns_detected: string[];
    recommendations: string[];
    learning_summary: string;
}

export class LearnTool implements vscode.LanguageModelTool<LearnInput> {
    public readonly name = 'sophia_learn';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<LearnInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { workspace_root, event_type, event_data } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/learn_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root,
                event_type,
                event_data
            ]);

            if (stderr) {
                console.error('Learn stderr:', stderr);
            }

            const result: LearnResult = JSON.parse(stdout);

            return {
                content: [
                    new vscode.LanguageModelTextPart(JSON.stringify(result, null, 2))
                ]
            };
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            return {
                content: [
                    new vscode.LanguageModelTextPart(
                        JSON.stringify({ error: `Learn failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<LearnInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: `Recording learning: ${options.input.event_type}`
        };
    }
}
