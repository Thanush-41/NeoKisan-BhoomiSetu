import React from 'react';
import { Button } from './Button';

interface QuantityDialogProps {
  open: boolean;
  min: number;
  max: number;
  value: number;
  onChange: (val: number) => void;
  onClose: () => void;
  onConfirm: () => void;
}

export const QuantityDialog: React.FC<QuantityDialogProps> = ({
  open,
  min,
  max,
  value,
  onChange,
  onClose,
  onConfirm,
}) => {
  const [inputError, setInputError] = React.useState<string | null>(null);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
      <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-xs">
        <h3 className="text-lg font-semibold mb-2">Select Quantity</h3>
        <input
          type="number"
          min={min}
          max={max}
          value={value === 0 ? '' : value}
          onChange={e => {
            const val = e.target.value === '' ? 0 : Number(e.target.value);
            setInputError(null);
            onChange(val);
          }}
          className="border rounded px-3 py-2 w-full mb-2"
        />
        {inputError && (
          <div className="text-xs text-red-600 mb-2">{inputError}</div>
        )}
        <div className="flex justify-end space-x-2">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={() => {
            if (!value || value < min) {
              setInputError(`Please enter a quantity of at least ${min}.`);
              return;
            }
            setInputError(null);
            onConfirm();
          }} disabled={value > max}>
            Add
          </Button>
        </div>
      </div>
    </div>
  );
};
