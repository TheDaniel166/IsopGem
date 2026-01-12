import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface AnticipateInput {
    workspace_root: string;
    task_description: string;
    context_hint?: string;
}

export interface AnticipateResult {
    task: string;
    preloaded_context: {
        dependencies: string[];
        relevant_files: string[];
        grimoires: string[];
        known_issues: string[];
        current_seals: Record<string, boolean>;
    };
    recommendations: string[];
    ready: boolean;
}

export class AnticipateTool implements vscode.LanguageModelTool<AnticipateInput> {
    public readonly name = 'sophia_anticipate';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<AnticipateInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { workspace_root, task_description, context_hint = '' } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/anticipate_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root,
                task_description,
                context_hint
            ]);

            if (stderr) {
                console.error('Anticipate stderr:', stderr);
            }

            const result: AnticipateResult = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Anticipate failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<AnticipateInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: `Pre-loading context for: ${options.input.task_description}`
        };
    }
}
