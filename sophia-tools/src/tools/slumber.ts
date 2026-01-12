import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface SlumberInput {
    chronicle: string;
    wisdom?: string[];
    skills?: string[];
    communication?: string;
    note_for_next?: string;
    workspace_root: string;
}

export interface SlumberOutput {
    success: boolean;
    session_number: number;
    archived: boolean;
    timestamp: string;
    message: string;
}

export class SlumberTool implements vscode.LanguageModelTool<SlumberInput> {
    public readonly name = 'sophia_slumber';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<SlumberInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const input = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/slumber_bridge.py');
            const inputJson = JSON.stringify(input);
            
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                input.workspace_root,
                inputJson
            ]);

            if (stderr) {
                console.error('Slumber stderr:', stderr);
            }

            const result: SlumberOutput = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Slumber failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<SlumberInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: 'Archiving session state and closing...'
        };
    }
}
