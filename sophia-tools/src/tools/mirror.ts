import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface MirrorInput {
    workspace_root: string;
    action: string;
    timeframe?: string;
    focus?: string;
}

export interface Pattern {
    type: string;
    description: string;
    evidence: string[];
    frequency: number;
    insight: string;
}

export interface MirrorResult {
    action: string;
    timeframe: string;
    patterns_detected: Pattern[];
    reflections: string[];
    suggestions: string[];
}

export class MirrorTool implements vscode.LanguageModelTool<MirrorInput> {
    public readonly name = 'sophia_mirror';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<MirrorInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { workspace_root, action, timeframe = 'week', focus } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/mirror_bridge.py');
            const args = [pythonScript, workspace_root, action];
            
            args.push('--timeframe', timeframe);
            if (focus) args.push('--focus', focus);
            
            const { stdout, stderr } = await execFileAsync('python3', args);

            if (stderr) {
                console.error('Mirror stderr:', stderr);
            }

            const result: MirrorResult = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Mirror failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<MirrorInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: `Reflecting on patterns: ${options.input.action}`
        };
    }
}
