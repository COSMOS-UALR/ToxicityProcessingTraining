from detoxify import Detoxify
from tqdm import tqdm
import argparse
import torch
import os



def main(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    #Validate model choice
    if args.model not in {'original', 'unbiased', 'multilingual'}:
        raise ValueError("Model must be one of 'original', 'unbiased', 'multilingual'")
    #validate input file
    if not os.path.isfile(args.input):
        raise ValueError(f"Input file does not exist. No file located at: {args.input}")
    if not args.input.endswith('.txt'):
        raise ValueError("Input file must be a .txt file")
    #validate output file
    if not args.output.endswith('.csv'):
        raise ValueError("Output file must be a .csv file")
    
    model = Detoxify(args.model, device=device)
    results = []

    #Read input file
    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.readlines()
    for line in tqdm(text, desc='Processing'):
        results.append(model.predict(line.strip()))
    
    #Write output file
    with open(args.output, 'w') as f:
        #Write header
        if args.model == 'original':
            f.write(','.join(['text', 'toxicity', 'severe_toxicity', 'obscene', 'threat', 'insult', 'identity_hate']) + '\n')
        elif args.model == 'unbiased':
            f.write(','.join(['text', 'toxicity', 'severe_toxicity', 'obscene', 'identity_attack', 'insult', 'threat', 'sexual_explicit']) + '\n')
        elif args.model == 'multilingual':
            f.write('text,toxicity\n')
        #Write results
        for line, result in zip(text, results):
            #Forcing csv friendly chars
            line = "".join(x for x in line if x.isalnum() or x in (" ", "#"))
            d = [line] + [str(round(x, 3)) for x in result.values()]
            f.write(','.join(d) + '\n')
    print(f"\nResults written to {args.output}")

 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="input file", required=True)
    parser.add_argument("--output", help="output file", required=True)
    parser.add_argument("--model", help="Model name: {'original', 'unbiased', 'multilingual'}", required=True)
    args = parser.parse_args()
    main(args)