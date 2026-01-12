import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface AwakenInput {
    workspace_root: string;
}

export interface AwakenOutput {
    session_number: number;
    memory_core: string;
    soul_diary_recent: string;
    notes_for_next: string;
    crash_detected: boolean;
    recovery_data?: string;
}

export class AwakenTool implements vscode.LanguageModelTool<AwakenInput> {
    public readonly name = 'sophia_awaken';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<AwakenInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { workspace_root } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/awaken_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root
            ]);

            if (stderr) {
                console.error('Awaken stderr:', stderr);
            }

            const result: AwakenOutput = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Awaken failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<AwakenInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: 'Loading session context from memory files...'
        };
    }
}
