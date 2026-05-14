import { useForm } from "@tanstack/react-form";

export function TaskSubmitForm(props: { onSubmit: (value: string) => void }) {
  const form = useForm({
    defaultValues: { prompt: "" },
    onSubmit: ({ value }) => props.onSubmit(value.prompt),
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        e.stopPropagation();
        void form.handleSubmit();
      }}
      className="flex gap-2"
    >
      <form.Field name="prompt">
        {(field) => (
          <input
            className="rounded border px-3 py-2 text-sm"
            value={field.state.value}
            onChange={(e) => field.handleChange(e.target.value)}
            placeholder="Dispatch a runtime task"
          />
        )}
      </form.Field>
      <button type="submit" className="rounded border px-3 py-2 text-sm">
        Submit
      </button>
    </form>
  );
}
